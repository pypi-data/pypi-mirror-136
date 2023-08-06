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

import datetime
import importlib
import yaml
import traceback
from typing import Dict, Any
import studyclient

from flask import current_app
from urllib.parse import urlparse


def dispatch_callback(callback_data: str, action_url: str, config: Dict[str, Any]):
    """
    Dispatch the callback to the appropriate backend.
    """
    callback_method_name = config.get("STUDYGOV_CALLBACK_METHOD")
    callback_function = CALLBACK_BACKENDS.get(callback_method_name, 'local')
    current_app.logger.error(f'Using callback function {callback_function} with data {callback_data}  and action_url {action_url}')

    # Remove non JSON serializable stuff from the config so things like celery won't choke on it
    cleaned_config = {}
    NoneType = type(None)
    for key, value in config.items():
        if isinstance(value, (bool, float, int, str, NoneType)):
            cleaned_config[key] = value
        elif isinstance(value, (tuple, list)) and all(isinstance(x, (bool, float, int, str, NoneType)) for x in value):
            cleaned_config[key] = value
        elif isinstance(value, dict) and all (isinstance(x, (bool, float, int, str, NoneType)) for x in value.values()):
            cleaned_config[key] = value
        elif isinstance(value, set):
            cleaned_config[key] = list(value)

    callback_function(callback_data, action_url, cleaned_config)


def master_callback(callback_data: str, action_url: str, config: Dict[str, Any]):
    # current_app.logging.error('Master callback: {action_url}')
    callback_data = yaml.safe_load(callback_data)
    action_parsed_url = urlparse(action_url)
    connection = studyclient.connect(f"{action_parsed_url.scheme}://{action_parsed_url.netloc}")
    action = connection.create_object(studyclient.Action, action_url)

    if callback_data is None:
        action.set_fields(
            return_value="No callback for state",
            success=True,
            end_time=datetime.datetime.now().isoformat()
        )
        return

    function = callback_data.pop('function')
    callback_module = importlib.import_module('.{}'.format(function), 'studygovernor.callbacks')
    callback = getattr(callback_module, function)

    # Get the experiment URL
    experiment = action.experiment

    try:
        if callback is not None:
            result = callback(experiment, action, config, **callback_data)
        else:
            result = None
    except Exception as exception:
        print('Encountered exception in callback: {}'.format(exception))
        traceback.print_exc()

        return_value = "{}\n\n{}".format(exception, traceback.format_exc())
        success = False
    else:
        # Store results
        return_value = result
        success = True
    finally:
        end_time = datetime.datetime.now()

    if isinstance(return_value, str):
        return_value = return_value[:65536]  # Clip to textfield length for MySQL

    print('Setting callback result for action')
    action.set_fields(
        return_value=return_value,
        success=success,
        end_time=end_time.isoformat()
    )


# Empty backends dictionary to be populated
CALLBACK_BACKENDS = {}

# Register the celery callback backend
from .backends import local_backend
from .backends import celery_backend
