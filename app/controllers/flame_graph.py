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

from os.path import join, getmtime
from app.common.error import InvalidFileError
from app.perf.flame_graph import perf_generate_flame_graph
from app.cpuprofile.flame_graph import cpuprofile_generate_flame_graph
from app.nflxprofile.flame_graph import nflxprofile_generate_flame_graph
from app.trace_event.flame_graph import trace_event_generate_flame_graph
from app import config


def generate_flame_graph(filename, file_type, range_start, range_end, package_name=False):
    file_path = join(config.PROFILE_DIR, filename)
    mtime = getmtime(file_path)
    if file_type == 'perf':
        return perf_generate_flame_graph(file_path, range_start, range_end)
    elif file_type == 'cpuprofile':
        return cpuprofile_generate_flame_graph(file_path, range_start, range_end)
    elif file_type == 'trace_event':
        return trace_event_generate_flame_graph(file_path, mtime, range_start, range_end)
    elif file_type == 'nflxprofile':
        return nflxprofile_generate_flame_graph(file_path, range_start, range_end, package_name)
    else:
        raise InvalidFileError('Unknown file type.')
