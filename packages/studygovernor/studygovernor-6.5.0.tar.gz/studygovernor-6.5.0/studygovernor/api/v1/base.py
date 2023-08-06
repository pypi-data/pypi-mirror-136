# Copyright 2017-2021 Biomedical Imaging Group Rotterdam, Departments of
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

from flask import Blueprint

from .. import RegisteredApi

blueprint = Blueprint('api_v1', __name__)

api = RegisteredApi(
    blueprint,
    version='1.0',
    title='Study Governor REST API version 1.0',
    description='The Study Governor is for tracking experiments and study resources.',
    default_mediatype='application/json'
)
