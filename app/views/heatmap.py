import json
from flask import Blueprint, request, jsonify
from app.util.heatmap import generate_heatmap

MOD_HEATMAP = Blueprint( \
    'heatmap', __name__, url_prefix='/heatmap' \
)

@MOD_HEATMAP.route("/", methods=['GET'])
def get_heatmap():
    filename = request.args.get('filename')
    rows = request.args.get('rows', None)
    if rows is not None:
        rows = int(rows)
    return jsonify(generate_heatmap(filename, rows))