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

from flask_restx import fields, Resource
from flask_security import http_auth_required


from .base import api
from .state import state_list, state_model
from ... import models
from ...fields import ObjectUrl
from ...util.helpers import get_object_from_arg

db = models.db


workflow_list = api.model('WorkflowList', {
    'workflows': fields.List(ObjectUrl('api_v1.workflow', attribute='id'))
})


@api.route('/workflows', endpoint='workflows')
class WorkflowListAPI(Resource):
    @http_auth_required
    @api.marshal_with(workflow_list)
    @api.response(200, 'Success')
    def get(self):
        workflows = models.Workflow.query.all()
        return {'workflows': workflows}


workflow_model = api.model('Workflow', {
    'uri': fields.Url,
    'label': fields.String,
})


@api.route('/workflows/<id>', endpoint='workflow')
class WorkflowAPI(Resource):
    @http_auth_required
    @api.marshal_with(workflow_model)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified workflow')
    def get(self, id=None):
        workflow = get_object_from_arg(id, models.Workflow, models.Workflow.label)
        return workflow


@api.route('/workflows/<workflow_id>/states', endpoint='workflow_states')
class WorkflowStateListAPI(Resource):
    @http_auth_required
    @api.marshal_with(state_list)
    @api.response(200, 'Success')
    def get(self, workflow_id=None):
        workflow = get_object_from_arg(workflow_id, models.Workflow, models.Workflow.label)
        return {'states': workflow.states}


@api.route('/workflows/<workflow_id>/states/<state_id>', endpoint='workflow_state')
class WorkflowStateAPI(Resource):
    @http_auth_required
    @api.marshal_with(state_model)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified state')
    def get(self, workflow_id=None, state_id=None):
        workflow = get_object_from_arg(workflow_id, models.Workflow, models.Workflow.label)
        state = get_object_from_arg(state_id, models.State, models.State.label, filters={models.State.workflow == workflow})
        return state
