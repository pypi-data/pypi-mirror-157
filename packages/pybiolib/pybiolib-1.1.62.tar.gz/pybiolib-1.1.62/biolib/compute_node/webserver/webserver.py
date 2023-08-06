# pylint: disable=unsubscriptable-object

import json
import os
import time
import tempfile
import shutil
import logging
from flask import Flask, request, Response, jsonify, after_this_request
from flask_cors import CORS  # type: ignore

from biolib import utils
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_binary_format import SavedJob
from biolib.compute_node.webserver import webserver_utils
from biolib.compute_node.cloud_utils.cloud_utils import CloudUtils
from biolib.compute_node.webserver.gunicorn_flask_application import GunicornFlaskApplication
from biolib.biolib_logging import logger, TRACE, logger_no_user_data
from biolib.compute_node.webserver.webserver_utils import get_job_compute_state_or_404

app = Flask(__name__)
CORS(app)

biolib_tmp_dir = tempfile.TemporaryDirectory()


@app.route('/hello/')
def hello():
    return 'Hello'


@app.route('/v1/job/', methods=['POST'])
def save_job():
    saved_job = json.loads(request.data.decode())

    # TODO: figure out why this shallow validate method is used
    if not webserver_utils.validate_saved_job(saved_job):
        return jsonify({'job': 'Invalid job'}), 400

    job_id = saved_job['job']['public_id']
    job_temporary_dir = os.path.join(biolib_tmp_dir.name, job_id)
    os.makedirs(job_temporary_dir)
    saved_job['BASE_URL'] = BiolibApiClient.get().base_url
    saved_job['job_temporary_dir'] = job_temporary_dir

    compute_state = webserver_utils.get_compute_state(webserver_utils.UNASSIGNED_COMPUTE_PROCESSES)
    compute_state['job_id'] = job_id
    compute_state['job'] = saved_job['job']
    compute_state['job_temporary_dir'] = job_temporary_dir

    webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id] = compute_state

    if utils.IS_RUNNING_IN_CLOUD:
        config = CloudUtils.get_webserver_config()
        saved_job['compute_node_info'] = config['compute_node_info']
        compute_state['cloud_job_id'] = saved_job['cloud_job']['public_id']
        compute_state['cloud_job'] = saved_job['cloud_job']

        webserver_utils.update_auto_shutdown_time()

    saved_job_bbf_package = SavedJob().serialize(json.dumps(saved_job))
    send_package_to_compute_process(job_id, saved_job_bbf_package)

    return '', 201


@app.route('/v1/job/<job_id>/start/', methods=['POST'])
def start_compute(job_id):
    module_input_package = request.data

    if 'AES-Key-String' in request.headers:
        compute_state = webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]
        compute_state['aes_key_string_b64'] = request.headers['AES-Key-String']

    send_package_to_compute_process(job_id, module_input_package)
    return '', 201


@app.route('/v1/job/<job_id>/', methods=['DELETE'])
def terminate_job(job_id: str) -> Response:
    compute_state = get_job_compute_state_or_404(job_id)
    # TODO: Consider BBF package
    compute_state['received_messages_queue'].put(b'CANCEL_JOB')
    return Response()


@app.route('/v1/job/<job_id>/status/')
def status(job_id):
    # TODO Implement auth token

    compute_state = get_job_compute_state_or_404(job_id)
    current_status = compute_state['status'].copy()
    response = jsonify(current_status)

    if current_status['status_updates']:
        webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['status']['status_updates'] = []

    if current_status['stdout_and_stderr_packages_b64']:
        webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['status']['stdout_and_stderr_packages_b64'] = []

    return response


@app.route('/v1/job/<job_id>/result/')
def result(job_id):
    compute_state = webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]
    result_is_ready = compute_state['progress'] == 95
    if result_is_ready:
        logger_no_user_data.debug(f'Job "{job_id}" result is being downloaded by the user...')
        job_temporary_dir = compute_state["job_temporary_dir"]
        module_output_path = f'{job_temporary_dir}/module_output.bbf'
        # Set the progress to 99 to inform other cleanup code that result is being downloaded
        compute_state['progress'] = 99

        @after_this_request
        def remove_job_temporary_dir(response):  # pylint: disable=unused-variable
            if os.path.exists(job_temporary_dir):
                logger_no_user_data.debug(f'Removing result dir after download from path: {job_temporary_dir}')
                shutil.rmtree(job_temporary_dir)
            return response

        return Response(open(module_output_path, 'rb'))

    else:
        logger_no_user_data.error(f'Webserver: Result for job {job_id} was not found returning 404')
        return '', 404


def send_package_to_compute_process(job_id, package_bytes):
    compute_state = get_job_compute_state_or_404(job_id)
    message_queue = compute_state['messages_to_send_queue']
    message_queue.put(package_bytes)


def start_webserver(port, host):
    def worker_exit(server, worker):  # pylint: disable=unused-argument
        active_compute_states = list(
            webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT.values()) + webserver_utils.UNASSIGNED_COMPUTE_PROCESSES
        logger.debug(f'Sending terminate signal to {len(active_compute_states)} compute processes')
        if active_compute_states:
            for compute_state in active_compute_states:
                if compute_state['worker_thread']:
                    compute_state['worker_thread'].terminate()
            time.sleep(2)
        return

    def post_fork(server, worker):  # pylint: disable=unused-argument
        logger.info('Started compute node')

        if utils.IS_RUNNING_IN_CLOUD:
            logger.debug('Initializing webserver...')
            config = CloudUtils.get_webserver_config()
            utils.IS_DEV = config['is_dev']
            BiolibApiClient.initialize(config['base_url'])

            CloudUtils.initialize()
            webserver_utils.start_auto_shutdown_timer()

    if logger.level == TRACE:
        gunicorn_log_level_name = 'DEBUG'
    elif logger.level == logging.DEBUG:
        gunicorn_log_level_name = 'INFO'
    elif logger.level == logging.INFO:
        gunicorn_log_level_name = 'WARNING'
    else:
        gunicorn_log_level_name = logging.getLevelName(logger.level)

    options = {
        'bind': f'{host}:{port}',
        'workers': 1,
        'post_fork': post_fork,
        'worker_exit': worker_exit,
        'timeout': '7200',  # Reduce to 300 when frontend no longer downloads from webserver
        'graceful_timeout': 4,
        'loglevel': gunicorn_log_level_name,
    }

    GunicornFlaskApplication(app, options).run()
