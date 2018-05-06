from flask import json, request, Blueprint
from evodoc.exception import DbException, ApiException
from evodoc.login import login, authenticate, check_token_exists
from evodoc.entity import User, UserToken, UserType
from evodoc.api import response_ok, response_err, response_ok_list, response_ok_obj, validate_token, validate_data
from datetime import datetime, timedelta

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('', methods=['GET'])
def get_user_by_id_action():
    """
    Get user data by it's id
    """
    try:
        token = request.args.get('token')
        user_id = request.args.get('user_id')
        validate_token(token)
        data = User.get_user_by_id(user_id)
        return response_ok_obj(data)
    except DbException as err:
        return response_err(err)
    except ApiException as err:
        return response_err(err)

@user.route('', methods=['DELETE'])
def delete_user():
    """
    Deletes user by it's id (only deactivation)
    """
    try:
        data = request.get_json()
        validate_data(data, {'token', 'user_id'})
        token = data['token']
        user_id = data['user_id']
        validate_token(token)
        user = User.get_user_by_id(user_id)
        User.deactivate_user_by_id(user.id)
        data = {
            "data": "done"
        }
        return response_ok(data)
    except DbException as err:
        return response_err(err)
    except ApiException as err:
        return response_err(err)

@user.route('', methods=['POST'])
def update_user():
    """
    Update user with suplied data, now works only for email, password, name and user type
        :param id: integer user id
    """
    try:
        data = request.get_json()
        validate_data(data, {'token', 'user_id'})
        user_id = data['user_id']
        token = data['token']
        validate_token(token)
        user = User.update_user_by_id_from_array(user_id, data)
        return response_ok_obj(user)
    except DbException as err:
        return response_err(err)
    except ApiException as err:
        return response_err(err)

@user.route('/all', methods=['GET'])
def get_user_all_action():
    """
    Get all user, only for logged users
    Token is taken from url param
    """
    try:
        token = request.args.get('token')
        validate_token(token)
        data = User.get_user_all()
        return response_ok_list(data)
    except DbException as err:
        return response_err(err)
    except ApiException as err:
        return response_err(err)

@user.route("/activation", methods=['POST'])
def activation_action():
    """
    Acc activation
    """
    try:
        data = request.get_json()
        validate_data(data, {'token'})
        token = check_token_exists(data['token'])
        if token == None:
            raise ApiException(403, "Invalid token")
        if token.user.activated:
            raise ApiException(401, "User has been already activated.")
        #check code somehow
        token.user.update_activation_by_id(token.user.id, True)
        data = {
            "data": "activated"
        }
        return response_ok(data)
    except ApiException as err:
        return response_err(err)
    except DbException as err:
        return response_err(err)

@user.route("/active", methods=['POST'])
def is_user_active():
    try:
        data = request.get_json()
        validate_data(data, {'token'})
        token = validate_token(data['token'])
        tokenData = {
            "token": token
        }
        return response_ok(tokenData)
    except ApiException as err:
        return response_err(err)
    except DbException as err:
        return response_err(err)

@user.route("/authorised", methods=['POST'])
def is_user_authorised():
    try:
        data = request.get_json()
        validate_data(data, {'token', 'user_id'})
        token = check_token_exists(data['token'])
        if token == None\
            or (token.created + timedelta(hours=24) < datetime.utcnow() \
            and token.update + timedelta(hours=2) < datetime.utcnow())\
            or token.user.active == False:
            raise ApiException(403, "user is not authorised")
        user_id = data['user_id']
        if (user_id != token.user_id):
            raise ApiException(403, "Invalid token")
        tokenData = {
            "token": token.token
        }
        return response_ok(tokenData)
    except ApiException as err:
        return response_err(err)
    except DbException as err:
        return response_err(err)
