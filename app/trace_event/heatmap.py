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
# TODO: handle CPU time differences, where "E" comes before "B"
#

import collections
import math
import json
from flask import abort

from app.common.fileutil import get_file
from app.trace_event.common import get_time_range

FREQUENCY = 100  # 100 Hz

# microsecond interval
u_sec_interval = int(1000000 / FREQUENCY)


def trace_event_read_offsets(file_path, mtime):
    try:
        f = get_file(file_path)
        profile = json.load(f)
    except ValueError:
        abort(500, 'Failed to parse profile.')
    finally:
        f.close()

    root_slices = []
    events = {}
    offsets = []

    (start_time, end_time) = get_time_range(file_path, mtime, profile)

    # process all events in the profile to extract root events
    for row in profile:
        key = str(row['pid']) + '_' + str(row['tid'])
        if row['ph'] == 'B' or row['ph'] == 'E':
            if row['ph'] == 'B':
                if key not in events:
                    events[key] = {'ts': row['ts'], 'tts': row['tts'], 'children_count': 0}
                else:
                    events[key]['children_count'] = events[key]['children_count'] + 1
            elif row['ph'] == 'E':
                if events[key]['children_count'] > 0:
                    events[key]['children_count'] = events[key]['children_count'] - 1
                else:
                    root_slices.append({'start': events[key]['ts'], 'cpu_start': events[key]['tts'], 'end': row['ts'], 'cpu_end': row['tts']})
                    del events[key]
        elif row['ph'] == 'X':
            if 'dur' in row and row['dur'] > 0 and 'tdur' in row and row['tdur'] > 0:
                if key not in events:  # it's a root event
                    root_slices.append({'start': row['ts'], 'cpu_start': row['tts'], 'end': row['ts'] + row['dur'], 'cpu_end': row['tts'] + row['tdur']})

    # process each root event and generate time offsets based on frequency
    for s in root_slices:
        first_index = math.floor(s['start'] / u_sec_interval) * u_sec_interval
        last_index = math.ceil(s['end'] / u_sec_interval) * u_sec_interval
        # TODO: user cpu usage
        # usage = (s['cpu_end'] - s['cpu_start']) / (s['end'] - s['start'])
        for i in range(first_index, last_index, u_sec_interval):
            offsets.append(i / 1000000)
    res = collections.namedtuple('offsets', ['start', 'end', 'offsets'])(start_time / 1000000, end_time / 1000000, offsets)
    return res
