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
from .experiment import experiment_list
from ... import models
from ...fields import ObjectUrl, SubUrl
from ...util.helpers import get_object_from_arg

state_list = api.model('StateList', {
    'states': fields.List(ObjectUrl('api_v1.state', attribute='id'))
})


@api.route('/states', endpoint='states')
class StateListAPI(Resource):
    @http_auth_required
    @api.marshal_with(state_list)
    @api.response(200, 'Success')
    def get(self):
        states = models.State.query.all()
        return {'states': states}


state_model = api.model('State', {
    'uri': fields.Url,
    'label': fields.String,
    'callback': fields.String,
    'lifespan': fields.Integer,
    'freetext': fields.String,
    'workflow': ObjectUrl('api_v1.workflow', attribute='workflow_id'),
    'experiments': SubUrl('api_v1.state', 'experiments', attribute='id')
})


@api.route('/states/<id>', endpoint='state')
class StateAPI(Resource):
    @http_auth_required
    @api.marshal_with(state_model)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified state')
    def get(self, id=None):
        state = get_object_from_arg(id, models.State, models.State.label)
        return state


@api.route('/states/<id>/experiments', endpoint='state_experiments')
class StateExperimentsAPI(Resource):
    @http_auth_required
    @api.marshal_with(experiment_list)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified state')
    def get(self, id=None):
        try:
            id = int(id)
            state = models.State.query.filter(models.State.id == id).one_or_none()
        except ValueError:
            state = models.State.query.filter(models.State.label == id).one_or_none()

        if state is None:
            abort(404)
        return {'experiments': state.experiments}

