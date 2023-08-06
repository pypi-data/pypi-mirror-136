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
from flask_security import http_auth_required, permissions_accepted


from .base import api
from ... import models
from ...fields import ObjectUrl

db = models.db


role_get = api.model("RoleGet", {
    'name': fields.String,
    'description': fields.String,
    'update_datetime': fields.DateTime,
    'permissions': fields.List(fields.String)
})


role_list_get = api.model("RoleListGet", {
    'roles': fields.List(ObjectUrl('api_v1.role', attribute='id'))
})


@api.route('/roles', endpoint='roles')
class RoleListAPI(Resource):
    @http_auth_required
    @permissions_accepted('roles_manage')
    @api.marshal_with(role_list_get)
    @api.response(200, "Success")
    def get(self):
        roles = models.Role.query.all()
        return {"roles": roles}


@api.route('/roles/<id>', endpoint='role')
class RoleApi(Resource):
    @http_auth_required
    @permissions_accepted('roles_manage')
    @api.marshal_with(role_get)
    @api.response(200, "Success")
    @api.response(404, "Could not find role")
    def get(self, id):
        role = models.Role.query.filter_by(id=id).one_or_none()
        if role is None:
            abort(404)
        return {'name': role.name,
                'description': role.description,
                'update_datetime': role.update_datetime,
                'permissions': role.get_permissions()}

