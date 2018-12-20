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

import os
import re
import magic
import gzip
from os.path import abspath
from app.common.error import InvalidFileError
from app import config

invalidchars = re.compile('[^a-zA-Z0-9.,/_%+: -\\\\]')

def validpath(file_path):
    if invalidchars.search(file_path):
        return False
    if not os.path.exists(file_path):
        return False
    return True


def get_file_mime(file_path):
    return magic.from_file(file_path, mime=True)


def get_file(file_path):
    # ensure the file is below PROFILE_DIR:
    if not abspath(file_path).startswith(abspath(config.PROFILE_DIR)):
        raise InvalidFileError("File %s is not in PROFILE_DIR" % file_path)
    if not validpath(file_path):
        raise InvalidFileError("Invalid characters or file %s does not exist." % file_path)

    mime = get_file_mime(file_path)

    if mime == 'application/gzip':
        return gzip.open(file_path, 'rt')
    elif mime == 'text/plain':
        return open(file_path, 'r')
    else:
        raise InvalidFileError('Unknown mime type.')
