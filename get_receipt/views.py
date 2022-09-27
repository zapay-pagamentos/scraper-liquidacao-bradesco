from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required
)
from .helpers import log
from marshmallow import Schema, fields, ValidationError
from .tasks import get_receipt_task
import os


get_receipt_blueprint = Blueprint('get-receipt', __name__)


@get_receipt_blueprint.route('/')
@jwt_required
def index():
    return dict(status='ok'), 200


@get_receipt_blueprint.route('/bradesco-receipts', methods=['GET'])
@jwt_required
def get_bradesco_receipts():
    data = request.get_json()
    if not data['renavams_list']:
        message = "Data cannot be null"
        log(message)
        return dict(message=message), 404
    if not data['state']:
        message = "State cannot be null"
        log(message)
        return dict(message=message), 404
    else:
        log("Get bradesco receipts")
        renavams_list = data.get('renavams_list')
        state = data.get('state')
        get_receipt_task.delay(renavams_list, state)
        return dict(status="OK"), 200


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


@get_receipt_blueprint.route('/login', methods=['POST'])
def login():
    username = os.environ.get('RECEIPT_BRADESCO_USER')
    password = os.environ.get('RECEIPT_BRADESCO_KEY')
    form = LoginSchema()
    try:
        result = form.load(request.json)
        if(
            username != result['username'] and
            password != result['password']
        ):
            return dict(success=False, errors="Bad username or password"), 401
    except ValidationError as error:
        return dict(success=False, errors=error.messages), 400

    access_token = create_access_token(identity=result['username'])
    return dict(access_token=access_token), 200
