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
from app.controllers.differential import generate_differential_flame_graph

MOD_DIFFERENTIAL_FLAME_GRAPH = Blueprint(
    'differential', __name__, url_prefix='/differential'
)


@MOD_DIFFERENTIAL_FLAME_GRAPH.route("/", methods=['GET'])
def get_differential_flame_graph():
    filename = request.args.get('filename')
    file_type = request.args.get('type')
    compare_filename = request.args.get('compareFilename')
    compare_type = request.args.get('compareType')
    start = request.args.get('start', None)
    if start is not None:
        start = float(start)
    end = request.args.get('end', None)
    if end is not None:
        end = float(end)
    compare_start = request.args.get('compareStart', None)
    if compare_start is not None:
        compare_start = float(compare_start)
    compare_end = request.args.get('compareEnd', None)
    if compare_end is not None:
        compare_end = float(compare_end)

    differential_flame_graph = generate_differential_flame_graph(
        filename, file_type, compare_filename, compare_type, start, end, compare_start, compare_end)
    return jsonify(differential_flame_graph)
