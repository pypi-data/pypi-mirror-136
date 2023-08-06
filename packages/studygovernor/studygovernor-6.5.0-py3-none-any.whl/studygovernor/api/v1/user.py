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
from flask_security import auth_required, http_auth_required, permissions_accepted, current_user


from .base import api
from ... import models, user_datastore
from ...fields import ObjectUrl
from ...util.helpers import hash_password, has_permission_any, get_object_from_arg

db = models.db


user_list_get = api.model("UserListGet", {
    'users': fields.List(ObjectUrl('api_v1.user', attribute='id'))
})


user_get = api.model("UserGet", {
    'username': fields.String,
    'uri': fields.Url('api_v1.user'),
    'name': fields.String,
    'active': fields.Boolean,
    'email': fields.String,
    'create_time': fields.DateTime,
})


user_put = api.model("UserPut", {
    'username': fields.String,
    'name': fields.String,
    'active': fields.Boolean,
    'email': fields.String,
    'password': fields.String,
})


@api.route('/users', endpoint='users')
class UserListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('username', type=str, required=True, location='json')
    request_parser.add_argument('password', type=str, required=True, location='json')
    request_parser.add_argument('name', type=str, required=True, location='json')
    request_parser.add_argument('email', type=str, required=True, location='json')
    request_parser.add_argument('active', type=bool, required=False, default=True, location='json')

    @http_auth_required
    @permissions_accepted('user_read_all')
    @api.marshal_with(user_list_get)
    @api.response(200, "Success")
    def get(self):
        users = models.User.query.all()
        return {'users': users}

    @http_auth_required
    @permissions_accepted('user_add')
    @api.marshal_with(user_get)
    @api.expect(user_put)
    @api.response(201, "Created user")
    def post(self):
        args = self.request_parser.parse_args()
        args['password'] = hash_password(args['password'])
        user = user_datastore.create_user(**args)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user, 201


@api.route('/users/<id>', endpoint='user')
class UserAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('username', type=str, required=False, location='json')
    request_parser.add_argument('password', type=str, required=False, location='json')
    request_parser.add_argument('name', type=str, required=False, location='json')
    request_parser.add_argument('email', type=str, required=False, location='json')
    request_parser.add_argument('active', type=bool, required=False, location='json')

    @http_auth_required
    @permissions_accepted('user_read', 'user_read_all')
    @api.marshal_with(user_get)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    @api.response(404, "Could not find user")
    def get(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()

        if not has_permission_any('user_read_all'):
            if user != current_user:
                abort(403, "You are not authorized to get this information")

        if user is None:
            abort(404)

        return user

    @http_auth_required
    @permissions_accepted('user_update_all')
    @api.marshal_with(user_get)
    @api.expect(user_put)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to perform this operation")
    @api.response(404, "Could not find user")
    def put(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()
        if user is None:
            abort(404)

        args = self.request_parser.parse_args()

        if args['username'] is not None:
            user.username = args['username']

        if args['password'] is not None:
            user.password = args['password']

        if args['name'] is not None:
            user.name = args['name']

        if args['active'] is not None:
            user.active = args['active']

        if args['email'] is not None:
            user.email = args['email']

        db.session.commit()
        db.session.refresh(user)

        return user

    @http_auth_required
    @permissions_accepted('user_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find user")
    def delete(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()

        if user is None:
            abort(404)

        user.active = False
        db.session.commit()


@api.route('/users/<user_id>/roles/<role_id>', endpoint='userrole')
class UserRoleAPI(Resource):
    @auth_required('session', 'basic')
    @permissions_accepted('roles_manage')
    @api.response(200, "Success")
    @api.response(404, "User or Role not found")
    def put(self, user_id, role_id):
        role = get_object_from_arg(role_id, models.Role, models.Role.name)
        user = get_object_from_arg(user_id, models.User, models.User.username)

        if user not in role.users:
            role.users.append(user)
            db.session.commit()
            db.session.refresh(role)

        return {"role": role.id, "user": user.id, "has_role": user in role.users}

    @auth_required('session', 'basic')
    @permissions_accepted('roles_manage')
    @api.response(200, "Success")
    @api.response(404, "User or Role not found")
    def delete(self, user_id, role_id):
        role = get_object_from_arg(role_id, models.Role, models.Role.name)
        user = get_object_from_arg(user_id, models.User, models.User.username)

        user.roles = [x for x in user.roles if x != role]
        db.session.commit()
        db.session.refresh(user)
        db.session.refresh(role)

        return {"role": role.id, "user": user.id, "has_role": user in role.users}
