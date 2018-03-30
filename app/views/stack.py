import json
from app.util.stack import generate_stack, get_stack_list
from flask import Blueprint, request, jsonify

MOD_STACK = Blueprint( \
    'stack', __name__, url_prefix='/stack' \
)

@MOD_STACK.route("/list", methods=['GET'])
def get_list():
    return jsonify(get_stack_list())

@MOD_STACK.route("/", methods=['GET'])
def get_stack():
    filename = request.args.get('filename')
    range_start = request.args.get('start', None)
    range_end = request.args.get('end', None)
    return jsonify(generate_stack(filename, range_start, range_end))