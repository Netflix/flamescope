import os
import re
import collections
from regexp import event_regexp, idle_regexp, comm_regexp, frame_regexp
from flask import abort
from app import config
from os import listdir
from os.path import isfile, join
from app import config
from math import ceil, floor

def get_stack_list():
    files = [f for f in listdir(config.STACK_DIR) if isfile(join(config.STACK_DIR, f))]
    return files

# get sample start and end
def calculate_stack_range(filename):
    start = float("+inf")
    end = float("-inf")
    path = config.STACK_DIR + '/' + filename

    # read .gz files via a "gunzip -c" pipe
    if filename.endswith(".gz"):
        try:
            f = os.popen("gunzip -c " + path)
        except:
            print("ERROR: Can't gunzip -c stack file, %s." % path)
            f.close()
            return abort(500)
    else:
        try:
            f = open(path, 'r')
        except:
            print("ERROR: Can't read stack file, %s." % path)
            f.close()
            return abort(500)
    
    for line in f.readlines():
        if (line[0] == '#'):
            continue
        r = re.search(event_regexp, line)
        if (r):
            ts = float(r.group(1))
            if (ts < start):
                start = ts
            elif (ts > end):
                end = ts
    
    f.close()

    return collections.namedtuple('range',['start', 'end'])(floor(start), ceil(end))

def library2type(library):
    if library == "":
        return ""
    if library.startswith("/tmp/perf-"):
        return "jit"
    if library.startswith("["):
        return "kernel"
    if library.find("vmlinux") > 0:
        return "kernel"
    return "user"

# add a stack to the root tree
def add_stack(root, stack):
    root['v'] += 1
    last = root
    for pair in stack:
        libtype = library2type(pair[1])
        found = 0
        for child in last['c']:
            if child['n'] == pair[0] and child['l'] == libtype:
                last = child
                found = 1
                break
        if (found):
            last['v'] += 1
        else:
            newframe = {}
            newframe['c'] = []
            newframe['n'] = pair[0]
            newframe['l'] = libtype
            newframe['v'] = 1
            last['c'].append(newframe)
            last = newframe
    return root

# return stack samples for a given range
def generate_stack(filename, range_start = None, range_end = None):
    path = config.STACK_DIR + '/' + filename

    # read .gz files via a "gunzip -c" pipe
    if filename.endswith(".gz"):
        try:
            f = os.popen("gunzip -c " + path)
        except:
            print("ERROR: Can't gunzip -c stack file, %s." % path)
            f.close()
            return abort(500)
    else:
        try:
            f = open(path, 'r')
        except:
            print("ERROR: Can't read stack file, %s." % path)
            f.close()
            return abort(500)

    # calculate stack file range
    r = calculate_stack_range(filename)
    start = r.start
    end = r.end

    # check range. default to full range if not specified.
    if (range_end):
        if ((start + float(range_end)) > end):
            print("ERROR: Bad range, %s -> %s." % str(start), str(end))
            return abort(416)
        else:
            end = start + float(range_end)
    if (range_start):
        start = start + float(range_start)

    if (start > end):
        print("ERROR: Bad range, %s -> %s." % str(start), str(end))
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

    # process perf script output and search for two things:
    # - event_regexp: to identify event timestamps
    # - idle_regexp: for filtering idle stacks
    for line in f.readlines():
        if (line[0] == '#'):
            continue
        r = re.search(event_regexp, line)
        if (r):
            if (stack):
                # process prior stack
                stackstr = ""
                for pair in stack:
                    stackstr += pair[0] + ";"
                if (re.search(idle_regexp, stackstr)):
                    # skip idle
                    stack = []
                elif (ts >= start and ts <= end):
                    root = add_stack(root, stack)
                stack = []
            ts = float(r.group(1))
            if (ts > end + overscan):
                break
            r = re.search(comm_regexp, line)
            if (r):
                comm = r.group(1).rstrip()
                stack.append([comm, ""])
            else:
                stack.append(["<unknown>", ""])
        else:
            r = re.search(frame_regexp, line)
            if (r):
                name = r.group(1)
                # strip leading "L" from java symbols:
                if (comm == "java" and name.startswith("L")):
                    name = name[1:]
                # strip instruction offset (+0xfe200...)
                c = name.find("+")
                if (c > 0):
                    name = name[:c]
                # strip symbol args (...):
                c = name.find("(")
                if (c > 0):
                    name = name[:c]
                stack.insert(1, [name, r.group(2)])
    # last stack
    if (ts >= start and ts <= end):
        root = add_stack(root, stack)

    # close file
    f.close()

    return root
