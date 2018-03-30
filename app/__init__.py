#!/usr/bin/python
#
# flamescope	Explore trace files with heat maps and flame graphs.
#               Processes Linux "perf script" ouptut.
#
# Copyright 2018 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 23-Feb-2017	Brendan Gregg	Created this.
# 19-Feb-2018	   "      "     Rewrite Perl -> Python.

"""
Initialize application
"""

import os
from .views.stack import MOD_STACK
from .views.heatmap import MOD_HEATMAP

from flask import Flask, request, abort, jsonify

APP = Flask(__name__, \
    static_folder=os.getcwd() + '/app/public', static_url_path=''
)

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
