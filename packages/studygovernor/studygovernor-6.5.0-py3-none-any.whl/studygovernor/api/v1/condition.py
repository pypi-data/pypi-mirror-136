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

condition_list = api.model('ConditionList', {
    'conditions': fields.List(ObjectUrl('api_v1.condition', attribute='id'))
})


@api.route('/conditions', endpoint='conditions')
class ConditionListAPI(Resource):
    @http_auth_required
    @api.marshal_with(condition_list)
    @api.response(200, 'Success')
    def get(self):
        conditions = models.Condition.query.all()
        return {'conditions': conditions}


condition_get = api.model('ConditionGet', {
    'uri': fields.Url,
    'rule': fields.String,
    'freetext': fields.String,
})


@api.route('/conditions/<int:id>', endpoint='condition')
class ConditionAPI(Resource):
    @http_auth_required
    @api.marshal_with(condition_get)
    @api.response(200, 'Success')
    def get(self, id: int):
        condition = models.Condition.query.filter(models.Condition.id == id).one_or_none()
        if condition is None:
            abort(404)
        return condition

