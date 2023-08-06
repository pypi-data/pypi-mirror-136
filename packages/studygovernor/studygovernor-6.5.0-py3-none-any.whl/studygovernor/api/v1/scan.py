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
from flask_restx import fields, Resource, reqparse
from flask_security import http_auth_required, permissions_accepted


from .base import api
from ... import models
from ...fields import ObjectUrl
from ...util.helpers import get_object_from_arg

db = models.db


scan_list = api.model('ScanList', {
    'scans': fields.List(ObjectUrl('api_v1.scan', attribute='id'))
})

scan_get = api.model('ScanGet', {
    'uri': fields.Url,
    'scantype': ObjectUrl('api_v1.scantype', attribute='scantype_id')
})


@api.route('/scans', endpoint='scans')
class ScanListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('scantype', type=str, required=True, location='json',
                                help='No label specified')
    request_parser.add_argument('experiment', type=str, required=True, location='json',
                                help='No date_of_birth specified')

    @http_auth_required
    @api.marshal_with(scan_list)
    @api.response(200, 'Success')
    def get(self):
        scans = models.Scan.query.all()
        return {'scans': scans}

    @http_auth_required
    @permissions_accepted('sample_add')
    @api.marshal_with(scan_get)
    @api.response(201, 'Created')
    def post(self):
        args = self.request_parser.parse_args()

        # Find the id for the subject url
        experiment = args['experiment']
        experiment = get_object_from_arg(experiment, models.Experiment, models.Experiment.label)

        # Find the id for the subject url
        scantype = args['scantype']
        scantype = get_object_from_arg(scantype, models.Scantype, models.Scantype.protocol)

        scan = models.Scan(experiment=experiment, scantype=scantype)

        db.session.add(scan)
        db.session.commit()
        db.session.refresh(scan)

        return scan, 201


@api.route('/scans/<int:id>', endpoint='scan')
class ScanAPI(Resource):
    pass


scan_type_list = api.model('ScanTypeList', {
    'scantypes': fields.List(ObjectUrl('api_v1.scantype', attribute='id'))
})


@api.route('/scantypes', endpoint='scantypes')
class ScantypeListAPI(Resource):
    @http_auth_required
    @api.marshal_with(scan_type_list)
    @api.response(200, 'Success')
    def get(self):
        scantypes = models.Scantype.query.all()
        return {'scantypes': scantypes}


scan_type = api.model('ScanType', {
    'uri': fields.Url,
    'modality': fields.String,
    'protocol': fields.String,
})


@api.route('/scantypes/<int:id>', endpoint='scantype')
class ScantypeAPI(Resource):
    @http_auth_required
    @api.marshal_with(scan_type)
    @api.response(200, 'Success')
    @api.response(404, 'Could not find specified scantype')
    def get(self, id):
        scantype = models.Scantype.query.filter(models.Scantype.id == id).one_or_none()
        if scantype is None:
            abort(404)
        return scantype

