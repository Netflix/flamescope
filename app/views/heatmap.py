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

from flask import Blueprint, request, jsonify, abort
from app.controllers.heatmap import generate_heatmap
from app.common.error import InvalidFileError

MOD_HEATMAP = Blueprint(
    'heatmap', __name__, url_prefix='/heatmap'
)


@MOD_HEATMAP.route("/", methods=['GET'])
def get_heatmap():
    filename = request.args.get('filename')
    file_type = request.args.get('type')
    rows = request.args.get('rows', None)
    if rows is not None:
        rows = int(rows)
    try:
        heatmap = generate_heatmap(filename, file_type, rows)
        return jsonify(heatmap)
    except InvalidFileError as err:
        abort(500, err.message)
