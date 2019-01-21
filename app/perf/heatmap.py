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
from .regexp import event_regexp, idle_regexp
from app.common.fileutil import get_file


# read and cache offsets
def perf_read_offsets(file_path):
    start = float("+inf")
    end = float("-inf")
    offsets = []

    f = get_file(file_path)

    stack = ""
    ts = -1

    # process perf script output and search for two things:
    # - event_regexp: to identify event timestamps
    # - idle_regexp: for filtering idle stacks
    # this populates start, end, and offsets
    for line in f:
        if (line[0] == '#'):
            continue
        r = event_regexp.search(line)
        if (r):
            if (stack != ""):
                # process prior stack
                if (not idle_regexp.search(stack)):
                    offsets.append(ts)
                # don't try to cache stacks (could be many Gbytes):
                stack = ""
            ts = float(r.group(1))
            if (ts < start):
                start = ts
            stack = line.rstrip()
        else:
            stack += line.rstrip()
    # last stack
    if (not idle_regexp.search(stack)):
        offsets.append(ts)
    if (ts > end):
        end = ts

    f.close()

    res = collections.namedtuple('offsets', ['start', 'end', 'offsets'])(start, end, offsets)
    return res
