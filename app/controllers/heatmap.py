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

from math import ceil, floor
from os.path import join, getmtime
from app import config
from app.perf.heatmap import perf_read_offsets
from app.cpuprofile.heatmap import cpuprofile_read_offsets
from app.nflxprofile.heatmap import nflxprofile_readoffsets
from app.trace_event.heatmap import trace_event_read_offsets
from app.common.error import InvalidFileError

# global defaults
YRATIO = 1000  # milliseconds
DEFAULT_ROWS = 50

# global cache
offsets_cache = {}
offsets_mtimes = {}


def _read_offsets(file_path, file_type):
    # fetch modification timestamp and check cache
    mtime = getmtime(file_path)
    if file_path in offsets_cache:
        if mtime == offsets_mtimes[file_path]:
            # use cached heatmap
            return offsets_cache[file_path]
    if file_type == 'perf':
        return perf_read_offsets(file_path)
    elif file_type == 'cpuprofile':
        return cpuprofile_read_offsets(file_path)
    elif file_type == 'trace_event':
        return trace_event_read_offsets(file_path, mtime)
    elif file_type == 'nflxprofile':
        return nflxprofile_readoffsets(file_path)
    else:
        raise InvalidFileError('Unknown file type.')


# return a heatmap from the cached offsets
def generate_heatmap(filename, file_type, rows=None):
    file_path = join(config.PROFILE_DIR, filename)
    (start, end, offsets) = _read_offsets(file_path, file_type)
    maxvalue = 0

    if rows is None:
        rows = DEFAULT_ROWS

    rowoffsets = []
    for i in range(0, rows):
        rowoffsets.append(YRATIO * (float(i) / rows))
    rowoffsets.reverse()
    cols = int(ceil(end) - floor(start))
    timeoffsets = list(range(0, cols))
    # init cells (values) to zero
    values = []
    for i in range(0, cols):
        emptycol = []
        for i in range(0, rows):
            emptycol.append(0)
        values.append(emptycol)
    # increment heatmap cells
    for ts in offsets:
        col = int(floor(ts - floor(start)))
        row = rows - int(floor(rows * (ts % 1))) - 1
        values[col][row] += 1
        if (values[col][row] > maxvalue):
            maxvalue = values[col][row]

    heatmap = {}
    heatmap['rows'] = rowoffsets
    heatmap['columns'] = timeoffsets
    heatmap['values'] = values
    heatmap['maxvalue'] = maxvalue

    return heatmap
