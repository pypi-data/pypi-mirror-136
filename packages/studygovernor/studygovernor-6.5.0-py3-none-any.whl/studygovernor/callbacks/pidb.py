# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import urllib.parse
from typing import Union, List, Dict, Any

import yaml
import xnat
import taskclient
from studyclient import Experiment, Action

from studygovernor.services.pidb import pidbservice


def safe_update_state(experiment: Experiment, state: str):
    print(f'Update state for {experiment} to {state}')
    try:
        experiment.set_state(state)
        message = f"Upated state for {experiment} to {state}"
    except Exception as exception:
        message = f'Encountered error when trying to update the state of {experiment} to {state}: {exception}'
        print(message)
    return message


def download(url: str):
    # Find host to connect to
    split_url = urllib.parse.urlparse(url)
    host = urllib.parse.urlunparse(split_url._replace(path='', params='', query='', fragment=''))

    with xnat.connect(host, verify=False) as session:
        path = split_url.path

        resource, filename = path.split('/files/')
        print('Found desired filename: {}'.format(filename))
        if '{timestamp}' in path:
            pattern = filename.format(timestamp=r'(_?(?P<timestamp>\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d:\d\d)_?)?') + '$'
        else:
            pattern = filename + '$'

        # Query all files and sort by timestamp
        files = session.get_json('{}/files'.format(resource))
        files = [x['Name'] for x in files['ResultSet']['Result']]
        print('Found file candidates {}, pattern is {}'.format(files, pattern))
        files = {re.match(pattern, x): x for x in files}
        files = {k.group('timestamp'): v for k, v in files.items() if k is not None}
        print('Found files: {}'.format(files))

        if len(files) == 0:
            return None

        # None is the first, timestamp come after that, so last one is highest timestamp
        latest_file = sorted(files.items())[-1][1]
        print('Select {} as being the latest file'.format(latest_file))

        # Construct the correct path again
        path = '{}/files/{}'.format(resource, latest_file)

        data = session.get_json(path)

    return data


def pidb(experiment: Experiment,
         action: Action,
         config: Dict[str, Any],
         fields_uri: Union[str, List[str]],
         templates: Union[str, List[str]],
         done_state: str,
         failed_state: str,
         pidb_external_system_name: str='PIDB',
         xnat_external_system_name: str='XNAT',
         taskmanager_external_system_name: str='TASKMANAGER',
         **ignore):
    """
    Add experiment to IFDB

    :param experiment: Experiment,
    :param action: Action,
    :param fields_uri: Union[str, List[str]],
    :param templates: Union[str, List[str]],
    :param done_state: str,
    :param failed_state: str,
    :param pidb_external_system_name: str='IFDB',
    :param xnat_external_system_name: str='XNAT',
    :param taskmanager_external_system_name: str='TASKMANAGER'

    Example:

    .. code-block:: JSON

     {
        "function": "pidb",
        "fields_uri": [
          "resources/FIELDS/files/mask_{timestamp}.json",
          "resources/FIELDS/files/QA_{timestamp}.json"
        ],
        "templates": [
          "mask",
          "manual_qa"
        ],
        "done_state": "/data/states/done",
        "failed_state": "/data/states/write_inspect_data_failed"
     }
    """
    # Get required information
    print('Experiment located at: {}'.format(experiment))

    # Get subject
    subject = experiment.subject

    # Get XNAT information
    xnat_experiment_id = experiment.external_ids[xnat_external_system_name]
    xnat_subject_id = subject.external_ids[xnat_external_system_name]

    # Get external systems uris
    external_systems = experiment.session.external_systems
    xnat_uri = external_systems[xnat_external_system_name].url.rstrip('/')
    pidb_uri = external_systems[pidb_external_system_name].url.rstrip('/') + '/'  # Has to end with /
    taskmanager_uri = external_systems[taskmanager_external_system_name].url.rstrip('/')

    # Create URI path for XNAT experiment
    xnat_experiment_path = "data/archive/projects/{project}/subjects/{subject}/experiments/{experiment}".format(
        project=config['STUDYGOV_XNAT_PROJECT'],
        subject=xnat_subject_id,
        experiment=xnat_experiment_id
    )

    if not isinstance(fields_uri, list):
        fields_uri = [fields_uri]

    if not isinstance(templates, list):
        templates = [templates]

    log_data = []

    for fields, task_template in zip(fields_uri, templates):
        # Find URI for fields file
        xnat_fields_uri = '{}/{}/{}'.format(xnat_uri, xnat_experiment_path, fields)
        json_data = download(xnat_fields_uri)

        taskman = taskclient.connect(taskmanager_uri)
        task_template_data = taskman.get(f'/task_templates/{task_template}').json()
        task_template_data = yaml.safe_load(task_template_data['content'])

        log_data.append("""
    PIDB server: {}
    Subject id: {}
    Subject url: {}
    Experiment scandate: {}
    Generator url: {}
    Template name: {}
    
    JSON data: {} 
    
    Template JSON data: {}
    """.format(pidb_uri,
               subject.label,
               subject.external_uri(),
               experiment.label,
               experiment.scandate,
               action.external_uri().replace('/api/v1/', '/'),
               task_template,
               json_data,
               task_template_data))

        pidbservice.ingest_json(
            json_data,  # Fields file loaded and parsed
            task_template_data,  # Task template url/path/data?
            pidb_uri,  # IFDB url
            task_template,  # Name of the task template
            subject.label,  # For RSS this is ergo_id
            subject.external_uri(),  # Subject uri in study governor
            experiment.label,
            experiment.scandate,
            action.external_uri().replace('/api/v1/', '/')
        )

    result = True

    if result:
        print('SUCCESS')
        print('Calling callback with: {}'.format(done_state))
        log_data.append(safe_update_state(experiment, done_state))
    else:
        print('FAILED')
        print('Calling callback with: {}'.format(failed_state))
        log_data.append(safe_update_state(experiment, failed_state))

    log_data = '\n'.join(log_data)

    return log_data[:64000]

