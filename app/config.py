import os

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROFILE_DIR = 'examples'
HOST = os.getenv('FLAMESCOPE_HOST', '0.0.0.0')
PORT = os.getenv('FLAMESCOPE_PORT', 5050)
JSONIFY_PRETTYPRINT_REGULAR = False
