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

from flask import abort, current_app
from flask_restx import fields, Resource, reqparse, inputs
from flask_security import http_auth_required, permissions_accepted
from sqlalchemy.orm.exc import NoResultFound


from .base import api
from ... import models, control

from ...fields import ObjectUrl, MappingField

db = models.db

subject_list = api.model('SubjectList', {
    'subjects': fields.List(ObjectUrl('api_v1.subject', attribute='id'))
})

subject_get = api.model('SubjectGet', {
    'uri': fields.Url('api_v1.subject'),
    'label': fields.String,
    'date_of_birth': fields.String,
    'external_ids': MappingField,
    'experiments': fields.List(ObjectUrl('api_v1.experiment', attribute='id'))
})


subject_post = api.model('SubjectPost', {
    'label': fields.String,
    'date_of_birth': fields.String,
})


@api.route('/subjects', endpoint='subjects')
class SubjectListAPI(Resource):
    get_request_parser = reqparse.RequestParser()
    get_request_parser.add_argument('offset', type=int, required=False, location='args', help="Offset for pagination")
    get_request_parser.add_argument('limit', type=int, required=False, location='args', help="Maximum number of rows returned")

    request_parser = reqparse.RequestParser()
    request_parser.add_argument('label', type=str, required=True, location='json',
                                help='No label specified')
    request_parser.add_argument('date_of_birth', type=inputs.date, required=True, location='json',
                                help='No date_of_birth specified')

    @http_auth_required
    @api.marshal_with(subject_list)
    @api.response(200, 'Success')
    def get(self):
        args = self.get_request_parser.parse_args()
        offset = args['offset']
        limit = args['limit']

        subjects, count = control.get_subjects(offset=offset, limit=limit)
        return {
            'subjects': subjects,
            'offset': offset,
            'limit': limit,
            'count': count,
        }

    @http_auth_required
    @permissions_accepted('sample_add')
    @api.marshal_with(subject_get)
    @api.expect(subject_post)
    @api.response(201, 'Created')
    def post(self):
        current_app.logger.info("[INFO] About to post subject!")
        subject = models.Subject(**self.request_parser.parse_args())
        db.session.add(subject)
        db.session.commit()
        db.session.refresh(subject)

        return subject, 201


@api.route('/subjects/<id>', endpoint='subject')
class SubjectAPI(Resource):
    request_parser_get = api.parser()
    request_parser_get.add_argument('filter_field', type=str, required=False, location='args', help='Should be either "id" or "label"')

    request_parser_post = reqparse.RequestParser()
    request_parser_post.add_argument('label', type=str, required=False, location='json')
    request_parser_post.add_argument('date_of_birth', type=inputs.date, required=False, location='json')

    @http_auth_required
    @api.marshal_with(subject_get)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified subject')
    @api.expect(request_parser_get)
    def get(self, id):
        args = self.request_parser_get.parse_args()
        if args['filter_field'] == 'id':
            try:
                id_ = int(id)
                subject = models.Subject.query.filter(models.Subject.id == id_).one_or_none()
            except ValueError as excp:
                print(excp)
                subject = None
        elif args['filter_field'] == 'label':
            label = str(id)
            subject = models.Subject.query.filter(models.Subject.label == label).one_or_none()
        else:
            try:
                id_ = int(id)
                subject = models.Subject.query.filter(models.Subject.id == id_).one()
            except (ValueError, NoResultFound):
                label = str(id)
                subject = models.Subject.query.filter(models.Subject.label == label).one_or_none()

        if subject is None:
            abort(404)
        return subject

    @http_auth_required
    @permissions_accepted('sample_add')
    @api.marshal_with(subject_get)
    @api.expect(subject_post)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified subject')
    def put(self, id):
        args = self.request_parser_post.parse_args()
        subject = models.Subject.query.filter(models.Subject.id == id).one_or_none()

        if subject is None:
            abort(404)

        if args.get('label') is not None:
            subject.label = args['label']
        if args.get('date_of_birth') is not None:
            subject.date_of_birth = args['date_of_birth']

        db.session.commit()
        db.session.refresh(subject)

        return subject

