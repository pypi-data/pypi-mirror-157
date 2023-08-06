from urllib.parse import urlparse

from biolib import utils
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.compute_node.job_worker.executors.types import RemoteExecuteOptions

from biolib.compute_node.job_worker.job_storage import JobStorage


class RemoteExecutor:

    @staticmethod
    def execute_job(options: RemoteExecuteOptions, module_input_serialized: bytes) -> bytes:
        job_id = options['job']['public_id']
        cloud_job = BiolibJobApi.create_cloud_job(module_name='main', job_id=job_id)
        logger.debug(f"Cloud: Job created with id {cloud_job['public_id']}")

        node_url = cloud_job['compute_node_info']['url']
        if utils.BIOLIB_CLOUD_BASE_URL:
            logger_no_user_data.debug('Using cloud proxy URL from env var BIOLIB_CLOUD_BASE_URL')
            node_url = utils.BIOLIB_CLOUD_BASE_URL + urlparse(node_url).path

        logger_no_user_data.debug(f'Using compute node URL "{node_url}"')

        if utils.BASE_URL_IS_PUBLIC_BIOLIB:
            aes_key_string_b64 = JobStorage.generate_and_store_key_buffer_for_job(job_id)
            BiolibJobApi.start_cloud_job(job_id, module_input_serialized, node_url, aes_key_string_b64)
        else:
            BiolibJobApi.start_cloud_job(job_id, module_input_serialized, node_url)

        utils.STREAM_STDOUT = True
        BiolibJobApi.await_compute_node_status(
            compute_type='Cloud',
            node_url=node_url,
            retry_interval_seconds=1.5,
            retry_limit_minutes=10080,  # 1 Week
            status_to_await='Result Ready',
            job=options['job'],
        )

        BiolibApiClient.refresh_auth_token()
        return JobStorage.get_result(job=options['job'])
