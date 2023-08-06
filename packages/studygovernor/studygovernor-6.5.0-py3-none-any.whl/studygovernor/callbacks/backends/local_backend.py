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

import subprocess

from flask import current_app

from studygovernor.callbacks import CALLBACK_BACKENDS


def local_callback(callback_data: str, action_url: str, config=None):
    """
    This function dispatches a callback, at the moment it just creates a subprocess to handle the callback

    :param str callback_data: JSON string with description of the callback to use
    :param str action_url: the URL for the action that create the callback
    :param dict config: Copy of (most of) the flask app config
    :return:
    """
    # TODO: move this to a background watchdog thread that makes sure the program doesn't hang
    #       and can kill it when needed?
    current_app.logger.info('Local callback: {action_url}')
    callback_process = subprocess.Popen(['studygov-run-callback',
                                         '-c', callback_data,
                                         '-u', action_url])


CALLBACK_BACKENDS['local'] = local_callback

