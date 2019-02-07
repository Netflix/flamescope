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
from flask import abort
from os.path import getmtime
from math import ceil, floor
from app.perf.regexp import event_regexp, idle_regexp, comm_regexp, frame_regexp
from app.common.fileutil import get_file
from app.common.libtype import library2type

stack_times = {}        # cached start and end times for profiles
stack_mtimes = {}       # modification timestamp for profiles
stack_index = {}        # cached event times


# Get sample start and end, and populate stack_index for faster range lookup.
# At this point we've probably already made a pass through the profile file
# for generating its heatmap, so why not fetch these times then? Because we're
# supporting a stateless interface, and the user may start here.
def _get_profile_range(file_path):
    start = float("+inf")
    end = float("-inf")
    index_factor = 100      # save one timestamp per this many lines

    # check for cached times
    mtime = getmtime(file_path)
    if file_path in stack_times:
        if mtime == stack_mtimes[file_path]:
            return stack_times[file_path]

    f = get_file(file_path)

    linenum = -1
    stack_index[file_path] = []
    for line in f:
        linenum += 1
        # 1. Skip '#' comments
        # 2. Since we're only interested in the event summary lines, skip the
        # stack trace lines based on those that start with '\t'. This is a
        # performance optimization that avoids using the regexp needlessly,
        # and makes a large difference.
        if (line[0] == '#' or line[0] == '\t'):
            continue
        r = event_regexp.search(line)
        if (r):
            ts = float(r.group(1))
            if ((linenum % index_factor) == 0):
                stack_index[file_path].append([linenum, ts])
            if (ts < start):
                start = ts
            elif (ts > end):
                end = ts

    f.close()
    times = collections.namedtuple('range', ['start', 'end'])(floor(start), ceil(end))
    stack_times[file_path] = times
    stack_mtimes[file_path] = mtime

    return times


# add a stack to the root tree
def _add_stack(root, stack, comm):
    last = root
    for i, pair in enumerate(stack):
        # Split inlined frames. "->" is used by software such as java
        # perf-map-agent. For example, "a->b->c" means c() is inlined in b(),
        # and b() is inlined in a(). This code will identify b() and c() as
        # the "inlined" library type, and a() as whatever the library says
        # it is.
        names = pair[0].split('->')
        n = 0
        for j, name in enumerate(names):
            val = 0
            # only adding value to the top of the stack
            if i == (len(stack) - 1):
                if j == (len(names) - 1):
                    val = 1
            # strip leading "L" from java symbols (only reason we need comm):
            if (comm == "java" and name.startswith("L")):
                name = name[1:]
            libtype = library2type(pair[1]) if n == 0 else "inlined"
            n += 1
            found = 0
            for child in last['c']:
                if child['n'] == name and child['l'] == libtype:
                    last = child
                    found = 1
                    break
            if (found):
                last['v'] += val
            else:
                newframe = {}
                newframe['c'] = []
                newframe['n'] = name
                newframe['l'] = libtype
                newframe['v'] = val
                last['c'].append(newframe)
                last = newframe
    return root


# return stack samples for a given range
def perf_generate_flame_graph(file_path, range_start=None, range_end=None):
    # calculate profile file range
    r = _get_profile_range(file_path)
    start = r.start
    end = r.end

    # check range. default to full range if not specified.
    if (range_end):
        if ((start + range_end) > end):
            print("ERROR: Bad range, %s -> %s." % (str(start), str(end)))
            return abort(416)
        else:
            end = start + range_end
    if (range_start):
        start = start + range_start

    if (start > end):
        print("ERROR: Bad range, %s -> %s." % (str(start), str(end)))
        return abort(416)

    root = {}
    root['c'] = []
    root['n'] = "root"
    root['l'] = ""
    root['v'] = 0

    stack = []
    ts = -1
    comm = ""
    # overscan is seconds beyond the time range to keep scanning, which allows
    # for some out-of-order samples up to this duration
    overscan = 0.1

    # determine skip lines
    lastline = 0
    skiplines = 0
    if file_path in stack_index:
        for pair in stack_index[file_path]:
            if start < pair[1]:
                # scanned too far, use last entry
                skiplines = lastline
                break
            lastline = pair[0]

    f = get_file(file_path)

    # process perf script output and search for two things:
    # - event_regexp: to identify event timestamps
    # - idle_regexp: for filtering idle stacks
    linenum = -1
    for line in f:
        linenum += 1
        # Performance optimization. Makes a large difference.
        if (linenum < skiplines):
            continue
        # skip comments
        if (line[0] == '#'):
            continue

        # As a performance optimization, skip an event regexp search if the
        # line looks like a stack trace based on starting with '\t'. This
        # makes a big difference.
        r = None
        if (line[0] != '\t'):
            r = event_regexp.search(line)
        if (r):
            if (stack):
                # process prior stack
                stackstr = ""
                for pair in stack:
                    stackstr += pair[0] + ";"
                if (idle_regexp.search(stackstr)):
                    # skip idle
                    stack = []
                elif (ts >= start and ts <= end):
                    root = _add_stack(root, stack, comm)
                stack = []
            ts = float(r.group(1))
            if (ts > end + overscan):
                break
            r = comm_regexp.search(line)
            if (r):
                comm = r.group(1).rstrip()
                stack.append([comm, ""])
            else:
                stack.append(["<unknown>", ""])
        else:
            r = frame_regexp.search(line)
            if (r):
                name = r.group(1)
                # strip instruction offset (+0xfe200...)
                c = name.find("+")
                if (c > 0):
                    name = name[:c]
                stack.insert(1, [name, r.group(2)])
    # last stack
    if (ts >= start and ts <= end):
        root = _add_stack(root, stack, comm)

    # close file
    f.close()

    return root
