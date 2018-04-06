# This file is part of FlameScope, a performance analysis tool created by the
# Netflix cloud performance team. See:
#
#    https://github.com/Netflix/flamescope
#
# Copyright 2018 Netflix, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from flask import Blueprint, request, jsonify

from app.util.stack import generate_stack, get_stack_list

MOD_STACK = Blueprint(
    'stack', __name__, url_prefix='/stack'
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
