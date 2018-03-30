import os
import re
import time
import collections
from math import ceil, floor
from flask import abort
from regexp import event_regexp, idle_regexp
from app import config

# global defaults
YRATIO = 1000   # milliseconds
DEFAULT_ROWS = 50
heatmap_cache = {}
heatmap_mtimes = {}

# read and cache offsets
def read_offsets(filename):
    start = float("+inf")
    end = float("-inf")
    offsets = []
    path = config.STACK_DIR + '/' + filename

    # fetch modification timestamp and check cache
    try:
        mtime = os.path.getmtime(path)
    except:
        print("ERROR: Can't check file stats for %s." % path)
        return abort(500)
    if path in heatmap_cache:
        if mtime == heatmap_mtimes[path]:
            # use cached heatmap
            return heatmap_cache[path]

    # read .gz files via a "gunzip -c" pipe
    if filename.endswith(".gz"):
        try:
            f = os.popen("gunzip -c " + path)
        except:
            print("ERROR: Can't gunzip -c stack file %s." % path)
            f.close()
            return abort(500)
    else:
        try:
            f = open(path, 'r')
        except:
            print("ERROR: Can't read stack file %s." % path)
            f.close()
            return abort(500)

    stack = ""
    ts = -1
    # process perf script output and search for two things:
    # - event_regexp: to identify event timestamps
    # - idle_regexp: for filtering idle stacks
    # this populates start, end, and offsets
    for line in f.readlines():
        if (line[0] == '#'):
            continue
        r = re.search(event_regexp, line)
        if (r):
            if (stack != ""):
                # process prior stack
                if (not re.search(idle_regexp, stack)):
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
    if (not re.search(idle_regexp, stack)):
        offsets.append(ts)
    if (ts > end):
        end = ts

    f.close()

    heatmap = collections.namedtuple('offsets',['start', 'end', 'offsets'])(start, end, offsets)
    heatmap_cache[path] = heatmap
    heatmap_mtimes[path] = mtime
    return heatmap

# return a heatmap from the cached offsets
def generate_heatmap(filename, rows = None):
    o = read_offsets(filename)
    start = o.start
    end = o.end
    offsets = o.offsets
    maxvalue = 0

    if rows is None:
        rows = DEFAULT_ROWS

    rowoffsets = []
    for i in range(0, rows):
        rowoffsets.append(YRATIO * (float(i) / rows))
    rowoffsets.reverse()
    cols = int(ceil(end) - floor(start))
    timeoffsets = range(0, cols)
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
        row = rows - int(floor(rows * (ts % 1))) -1
        values[col][row] += 1
        if (values[col][row] > maxvalue):
            maxvalue = values[col][row]

    heatmap = {}
    heatmap['rows'] = rowoffsets
    heatmap['columns'] = timeoffsets
    heatmap['values'] = values
    heatmap['maxvalue'] = maxvalue

    return heatmap
