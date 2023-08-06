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
from flask_restx import fields, Resource, reqparse, inputs
from flask_security import http_auth_required, permissions_required

from .action import action_list
from .base import api
from ... import control, exceptions, models
from ...fields import ObjectUrl, SubUrl, MappingField
from ...util.helpers import get_object_from_arg

db = models.db


experiment_list = api.model('ExperimentList', {
    'experiments': fields.List(ObjectUrl('api_v1.experiment', attribute='id'))
})


experiment_get = api.model('ExperimentGet', {
    'uri': fields.Url('api_v1.experiment'),
    'subject': ObjectUrl('api_v1.subject', attribute='subject_id'),
    'label': fields.String,
    'scandate': fields.DateTime(dt_format='iso8601'),
    'state': SubUrl('api_v1.experiment', 'state', attribute='id'),
    'external_ids': MappingField
})


experiment_post = api.model('ExperimentPost', {
    'subject': ObjectUrl('api_v1.subject', attribute='subject_id'),
    'label': fields.String,
    'scandate': fields.DateTime(dt_format='iso8601'),
})


@api.route('/experiments', endpoint='experiments')
class ExperimentListAPI(Resource):
    # Request parser for the get function when filtering
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument('scandate', type=inputs.datetime_from_iso8601, required=False,
                                    location='args')
    get_request_parser.add_argument('subject', type=str, required=False,
                                    location='args')
    get_request_parser.add_argument('state', type=str, required=False,
                                    location='args')
    get_request_parser.add_argument('offset', type=int, required=False,
                                    location='args', help="Offset for pagination")
    get_request_parser.add_argument('limit', type=int, required=False,
                                    location='args', help="Maximum number of rows returned")

    # Request parser for when adding an experiment
    post_request_parser = reqparse.RequestParser()
    post_request_parser.add_argument('label', type=str, required=True, location='json',
                                     help='No label supplied')
    post_request_parser.add_argument('scandate', type=inputs.datetime_from_iso8601, required=True,
                                     location='json', help='No scandate supplied')
    post_request_parser.add_argument('subject', type=str, required=True, location='json',
                                     help='No subject supplied')
    post_request_parser.add_argument('workflow', type=str, required=False, location='json')

    @http_auth_required
    @api.marshal_with(experiment_list)
    @api.response(200, 'Success')
    def get(self):
        args = self.get_request_parser.parse_args()
        offset = args['offset']
        limit = args['limit']

        experiments, count = control.get_experiments(
            scandate=args['scandate'],
            subject=args['subject'],
            state=args['state'],
            offset=offset,
            limit=limit,
        )

        return {
            'experiments': experiments,
            'offset': offset,
            'limit': limit,
            'count': count,
        }

    @http_auth_required
    @permissions_required('sample_add')
    @api.marshal_with(experiment_get)
    @api.expect(experiment_post)
    @api.response(201, 'Created experiment')
    @api.response(404, 'Could not find specified subject')
    def post(self):
        args = self.post_request_parser.parse_args()

        # Find the id for the subject url
        subject = get_object_from_arg(args['subject'], models.Subject, models.Subject.label)
        if args['workflow'] is not None:
            workflow = get_object_from_arg(args['workflow'], models.Workflow, models.Workflow.label)
        else:
            workflow = models.Workflow.query.order_by(models.Workflow.id.desc()).first()

        # Post the experiment
        print('[DEBUG] Creating experiment {}'.format(args['label']))
        experiment = models.Experiment(workflow, label=args['label'], scandate=args['scandate'], subject=subject)
        db.session.add(experiment)
        db.session.commit()
        db.session.refresh(experiment)
        print('[DEBUG] EXPERIMENT: {}'.format(experiment.id))

        return experiment, 201


@api.route('/experiments/<id>', endpoint='experiment')
class ExperimentAPI(Resource):
    @http_auth_required
    @api.marshal_with(experiment_get)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find experiment')
    def get(self, id):
        try:
            id = int(id)
            experiment = models.Experiment.query.filter(models.Experiment.id == id).one_or_none()
        except ValueError:
            experiment = models.Experiment.query.filter(models.Experiment.label == id).one_or_none()

        if experiment is None:
            abort(404)
        return experiment


experiment_state_model = api.model('State', {
    'state': ObjectUrl('api_v1.state', attribute='id'),
    'workflow': ObjectUrl('api_v1.workflow', attribute='workflow_id'),

})

experiment_state_put_args = api.model('StatePutArgs', {
    'state': fields.String,
    'freetext': fields.String
})

experiment_state_put = api.model('StatePut', {
    'state': ObjectUrl('api_v1.state'),
    'error': fields.Raw,
    'success': fields.Boolean,
})


@api.route('/experiments/<int:id>/actions', endpoint='experiment_actions')
class ActionListAPI(Resource):
    @http_auth_required
    @api.marshal_with(action_list)
    @api.response(200, 'Success')
    def get(self, id: int):
        actions = models.Action.query.filter(models.Action.experiment_id == id).all()
        return {'actions': actions}


@api.route('/experiments/<int:id>/state', endpoint='experiment_state')
class ExperimentStateAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('state', type=str, required=True, location='json',
                                help='No state supplied')
    request_parser.add_argument('freetext', type=str, required=False, location='json',
                                help='Free text annotation for the created action')

    @http_auth_required
    @api.marshal_with(experiment_state_model)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified experiment')
    def get(self, id: int):
        experiment = get_object_from_arg(id, models.Experiment, models.Experiment.label)

        return experiment.state

    @http_auth_required
    @permissions_required('sample_state_update')
    @api.marshal_with(experiment_state_put)
    @api.expect(experiment_state_put_args)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified state')
    @api.response(409, 'Cannot change state to specified state, no valid transition!')
    def put(self, id):
        experiment = get_object_from_arg(id, models.Experiment, models.Experiment.label)
        current_workflow = experiment.state.workflow

        args = self.request_parser.parse_args()
        
        state = get_object_from_arg(
            args['state'],
            models.State,
            models.State.label, allow_none=True,
            filters={models.State.workflow: current_workflow}
        )

        if state is None:
            success = False
            error = {
                'errorclass': 'StateNotFoundError',
                'requested_state': args['state'],
                'message': 'Could not find requested state "{}"'.format(args['state']),
            }
            status = 404
        else:
            # Try to change the state
            try:
                experiment.set_state(state, 'api_v1', args['freetext'])
                success = True
                error = None
                status = 200
            except exceptions.StateChangeError as err:
                success = False
                error = err.marshal(api_prefix='api_v1')
                status = 409

        data = {
            'state': experiment.state.id,
            'error': error,
            'success': success,
        }

        print(experiment.state)

        return data, status
