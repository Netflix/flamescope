#!/usr/bin/python
#
# flamescope	Explore trace files with heat maps and flame graphs.
#               Processes Linux "perf script" ouptut.
#
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
#
# 23-Feb-2017	Brendan Gregg	Created this.
# 19-Feb-2018	   "      "     Rewrite Perl -> Python.
# 22-Mar-2018	Martin Spier	Split into Flask framework.

"""
Initialize application
"""

import os
from .views.stack import MOD_STACK
from .views.heatmap import MOD_HEATMAP

from flask import Flask, jsonify

APP = Flask(__name__,
            static_folder=os.getcwd() + '/app/public',
            static_url_path='')

APP.config.from_pyfile('config.py', silent=True)

@APP.route('/')
def root():
    return APP.send_static_file('index.html')

@APP.errorhandler(400)
def bad_request(err):
    """Return a custom 400 error."""
    # logging.error(err)
    return jsonify(error='The browser (or proxy) sent a request that this server could not understand.'), 400


@APP.errorhandler(404)
def page_not_found(err):
    """Return a custom 404 error."""
    # logging.error(err)
    return jsonify(error='Sorry, Nothing at this URL.'), 404


@APP.errorhandler(500)
def internal_error(err):
    """Return a custom 500 error."""
    return jsonify(error='Sorry, unexpected error: {}'.format(err)), 500


# Registering module blueprints
APP.register_blueprint(MOD_STACK)
APP.register_blueprint(MOD_HEATMAP)
