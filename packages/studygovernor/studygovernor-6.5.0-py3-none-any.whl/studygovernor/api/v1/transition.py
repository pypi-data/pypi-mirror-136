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

from flask import abort
from flask_restx import fields, Resource
from flask_security import http_auth_required


from .base import api
from ... import models

from ...fields import ObjectUrl

db = models.db

transition_list = api.model('TransitionList', {
    'transitions': fields.List(ObjectUrl('api_v1.transition', attribute='id'))
})


@api.route('/transitions', endpoint='transitions')
class TransitionListAPI(Resource):
    @http_auth_required
    @api.marshal_with(transition_list)
    @api.response(200, 'Success')
    def get(self):
        transitions = models.Transition.query.all()
        return {'transitions': transitions}


transition = api.model('Transition', {
    'uri': fields.Url,
    'destination_state': ObjectUrl('api_v1.state', attribute='destination_state_id'),
    'source_state': ObjectUrl('api_v1.state', attribute='source_state_id'),
    'conditions': fields.List(fields.String)
})


@api.route('/transitions/<int:id>', endpoint='transition')
class TransitionAPI(Resource):
    @http_auth_required
    @api.marshal_with(transition)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified transition')
    def get(self, id: int):
        transition = models.Transition.query.filter(models.Transition.id == id).one_or_none()
        if transition is None:
            abort(404)
        return transition
