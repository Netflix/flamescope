# This file is part of FlameScope, a performance analysis tool created by the
# Netflix cloud performance team. See:
#
#    https://github.com/Netflix/flamescope
#
# Copyright 2019 Netflix, Inc.
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

import collections
from flask import abort

from nflxprofile import nflxprofile_pb2
from app.common.fileutil import get_file


def nflxprofile_readoffsets(file_path):
    try:
        f = get_file(file_path)
        profile = nflxprofile_pb2.Profile()
        profile.ParseFromString(f.read())
    except TypeError:
        abort(500, 'Failed to parse profile.')
    finally:
        f.close()

    offsets = []
    current_time = profile.start_time

    for delta in profile.time_deltas:
        current_time += delta
        offsets.append(current_time)

    res = collections.namedtuple('offsets', ['start', 'end', 'offsets'])(profile.start_time, profile.end_time, offsets)
    return res
