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

import json
import math
from os.path import join
from app.common.fileutil import get_file
from app import config


def nflxprofile_generate_flame_graph(filename, range_start, range_end, profile=None):
    if not profile:
        file_path = join(config.PROFILE_DIR, filename)
        (f, mime) = get_file(file_path)
        profile = json.load(f)
        f.close()

    start_time = profile['startTime']
    if range_start is not None:
        adjusted_range_start = (math.floor(start_time) + range_start)
    if range_end is not None:
        adjusted_range_end = (math.floor(start_time) + range_end)

    return generate_flame_graph(profile['nodes'], profile['samples'], profile['timeDeltas'], profile['startTime'], adjusted_range_start, adjusted_range_end, None)