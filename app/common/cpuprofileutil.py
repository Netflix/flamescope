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

import collections
import math

def get_idle_id(nodes):
    for node in nodes:
        node_id = node['id']
        function_name = node['callFrame']['functionName']
        if function_name == '(idle)':
            return node_id


def cpuprofile_read_offsets(profile):
    time_deltas = profile['timeDeltas']
    samples = profile['samples']
    idle_id = get_idle_id(profile['nodes'])
    start_time = math.floor(profile['startTime'] / 1000000) * 1000000
    end_time = math.ceil(profile['endTime'] / 1000000) * 1000000

    offsets = []
    current_time = start_time

    for index, delta in enumerate(time_deltas):
        current_time += delta
        if samples[index] != idle_id:
            offsets.append(current_time / 1000000)

    res = collections.namedtuple('offsets', ['start', 'end', 'offsets'])(start_time / 1000000, end_time / 1000000, offsets)
    return res