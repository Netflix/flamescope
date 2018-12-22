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
import json
from json import JSONDecodeError
from os.path import abspath
from app.common.error import InvalidFileError
from app.perf.regexp import event_regexp
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


def is_perf_file(f):
    for line in f:
        if (line[0] == '#'):
            continue
        r = event_regexp.search(line)
        if r:
            return True
        return False


def get_file(file_path):
    # ensure the file is below PROFILE_DIR:
    if not abspath(file_path).startswith(abspath(config.PROFILE_DIR)):
        raise InvalidFileError("File %s is not in PROFILE_DIR" % file_path)
    if not validpath(file_path):
        raise InvalidFileError("Invalid characters or file %s does not exist." % file_path)

    mime = get_file_mime(file_path)

    if mime in ['application/x-gzip', 'application/gzip']:
        return gzip.open(file_path, 'rt')
    elif mime == 'text/plain':
        return open(file_path, 'r')
    else:
        raise InvalidFileError('Unknown mime type.')


def get_profile_type(file_path):
    f = get_file(file_path)
    if is_perf_file(f):
        f.close()
        return ('perf_script', None)
    else:
        try:
            f.seek(0)
            r = json.load(f)
            f.close()
            if isinstance(r, list):
                if 'ph' in r[0]:
                    return ('trace_event', r)
            elif 'nodes' in r:
                return ('cpuprofile', r)
            raise InvalidFileError('Unknown JSON file.')
        except JSONDecodeError:
            f.close()
            raise InvalidFileError('Unknown file type.')
