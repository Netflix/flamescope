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

import math
from flask import abort

from app.common.fileutil import get_file
from nflxprofile import nflxprofile_pb2
from nflxprofile.flamegraph import get_flame_graph, NodeJsStackProcessor, StackProcessor
from nflxprofile.flamegraph import NodeJsPackageStackProcessor


FLAVORS = {
    'standard': StackProcessor,
    'nodejs': NodeJsStackProcessor,
    'nodejs-packages': NodeJsPackageStackProcessor
}


def nflxprofile_generate_flame_graph(file_path, range_start, range_end, package_name=False, flavor='standard'):
    try:
        f = get_file(file_path)
        profile = nflxprofile_pb2.Profile()
        profile.ParseFromString(f.read())
    except TypeError:
        abort(500, 'Failed to parse profile.')
    finally:
        f.close()

    stack_processor = FLAVORS.get(flavor, StackProcessor)

    start_time = profile.start_time
    if range_start is not None:
        range_start = (math.floor(start_time) + range_start)
    if range_end is not None:
        range_end = (math.floor(start_time) + range_end)

    return get_flame_graph(profile, {}, range_start=range_start, range_end=range_end, package_name=package_name, stack_processor=stack_processor)


def nflxprofile_generate_differential_flame_graph(file_path, range_start, range_end):
    try:
        f = get_file(file_path)
        profile = nflxprofile_pb2.Profile()
        profile.ParseFromString(f.read())
    except TypeError:
        abort(500, 'Failed to parse profile.')
    finally:
        f.close()

    start_time = profile.start_time
    if range_start is not None:
        range_start = (math.floor(start_time) + range_start)
    if range_end is not None:
        range_end = (math.floor(start_time) + range_end)

    return get_flame_graph(profile, {}, range_start=range_start, range_end=range_end)
