# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biolib',
 'biolib.api',
 'biolib.app',
 'biolib.biolib_api_client',
 'biolib.biolib_binary_format',
 'biolib.biolib_docker_client',
 'biolib.biolib_singularity_client',
 'biolib.compute_node',
 'biolib.compute_node.cloud_utils',
 'biolib.compute_node.job_worker',
 'biolib.compute_node.job_worker.executors',
 'biolib.compute_node.job_worker.executors.remote',
 'biolib.compute_node.job_worker.executors.tars',
 'biolib.compute_node.webserver',
 'biolib.jobs',
 'biolib.templates',
 'biolib.user',
 'biolib.utils',
 'biolib.validators']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.3',
 'docker>=4.4.1',
 'flask-cors>=3.0.10',
 'flask>=2.0.1',
 'gunicorn>=20.1.0',
 'importlib-metadata>=1.6.1',
 'pycryptodome>=3.9.9',
 'pyjwt>=2.3.0',
 'pyyaml>=5.3.1',
 'requests>=2.25.1',
 'rich>=12.4.4,<13.0.0',
 'spython>=0.1.18']

extras_require = \
{':python_version < "3.8"': ['typing_extensions>=3.10.0',
                             'typing_inspect>=0.5.0,<0.6.0']}

entry_points = \
{'console_scripts': ['biolib = biolib:call_cli']}

setup_kwargs = {
    'name': 'pybiolib',
    'version': '1.1.73',
    'description': 'BioLib Python Client',
    'long_description': "# PyBioLib\n\nPyBioLib is a Python package for running BioLib applications from Python scripts and the command line.\n\n### Python Example\n```python\n# pip3 install -U pybiolib\nimport biolib\nsamtools = biolib.load('samtools/samtools')\nprint(samtools.cli(args='--help'))\n```\n\n### Command Line Example\n```bash\npip3 install -U pybiolib\nbiolib run samtools/samtools --help\n```\n\n",
    'author': 'biolib',
    'author_email': 'hello@biolib.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/biolib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.3,<4.0.0',
}


setup(**setup_kwargs)
