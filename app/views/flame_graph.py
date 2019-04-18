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
from app.controllers.flame_graph import generate_flame_graph

MOD_FLAME_GRAPH = Blueprint(
    'flamegraph', __name__, url_prefix='/flamegraph'
)


@MOD_FLAME_GRAPH.route("/", methods=['GET'])
def get_flame_graph():
    filename = request.args.get('filename')
    file_type = request.args.get('type')
    package_name = request.args.get('packageName', False)
    package_name = True if package_name and package_name == 'true' else False
    range_start = request.args.get('start', None)
    if range_start is not None:
        range_start = float(range_start)
    range_end = request.args.get('end', None)
    if range_end is not None:
        range_end = float(range_end)
    flame_graph = generate_flame_graph(filename, file_type, range_start, range_end, package_name)
    return jsonify(flame_graph)
