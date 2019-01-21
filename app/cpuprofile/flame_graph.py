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

import json
import math
import copy
from os.path import join
from app.common.fileutil import get_file
from app import config

class Node:
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.children = []

    def get_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add(self, stack, value):
        if len(stack) > 0:
            name = stack[0]
            child = self.get_child(name)
            if child is None:
                child = Node(name)
                self.children.append(child)
            child.add(stack[1:], value)
        else:
            self.value += value

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=2
        )


def parse_nodes(data):
    nodes = {}
    for node in data['nodes']:
        node_id = node['id']
        function_name = node['callFrame']['functionName']
        url = node['callFrame']['url']
        line_number = node['callFrame']['lineNumber']
        children = node.get('children')
        hit_count = node.get('hitCount')
        nodes[node_id] = {'function_name': function_name, 'url': url, 'line_number': line_number, 'hit_count': hit_count, 'children': children}
    return nodes


def generate_callgraph(root, node_id, ignore_ids, nodes, stack):
    node = nodes[node_id]  # break in case id doesn't exist
    if node['id'] not in ignore_ids:
        if node['function_name'] == '':
            node['function_name'] = '(anonymous)'
        stack.append(node['function_name'])
        if node['hit_count'] > 0:
            root.add(stack, node['hit_count'])
        if node['children']:
            for child in node['children']:
                generate_callgraph(root, child, ignore_ids, nodes, copy.copy(stack))
    del nodes[node_id]


def get_meta_ids(nodes):
    program_node_id = None
    idle_node_id = None
    gc_node_id = None
    for key, node in nodes.items():
        if node['function_name'] == '(program)':
            program_node_id = key
        elif node['function_name'] == '(idle)':
            idle_node_id = key
        elif node['function_name'] == '(garbage collector)':
            gc_node_id = key
    return program_node_id, idle_node_id, gc_node_id


def generate_stacks(node_id, nodes, stacks, current_stack):
    node = nodes[node_id]  # break in case id doesn't exist
    if node['function_name'] == '':
        node['function_name'] = '(anonymous)'
    if node['function_name'] != '(root)':
        current_stack.append(node['function_name'])
        stacks[node_id] = current_stack
    if node['children']:
        for child in node['children']:
            generate_stacks(child, nodes, stacks, copy.copy(current_stack))
    del nodes[node_id]


def cpuprofile_generate_flame_graph(filename, range_start, range_end, profile=None):
    if not profile:
        file_path = join(config.PROFILE_DIR, filename)
        f = get_file(file_path)
        profile = json.load(f)
        f.close()

    nodes = parse_nodes(profile)
    ignore_ids = get_meta_ids(nodes)

    root = Node('root')
    root_id = profile['nodes'][0]['id']

    # no range defined, just return the callgraph
    if range_start is None and range_end is None:
        generate_callgraph(root, root_id, nodes, [])
        return root

    samples = profile['samples']
    time_deltas = profile['timeDeltas']
    start_time = profile['startTime']
    #end_time = profile['endTime']
    adjusted_start = (math.floor(start_time / 1000000) + range_start) * 1000000
    adjusted_end = (math.floor(start_time / 1000000) + range_end) * 1000000
    current_time = start_time + time_deltas[0]
    stacks = {}
    generate_stacks(root_id, nodes, stacks, [])
    for index, sample in enumerate(samples):
        if index == (len(samples) - 1):  # last sample
            break
        delta = time_deltas[index + 1]
        if delta < 0:  # TODO: find a better way to deal with negative time deltas
            delta = 0
            continue
        current_time += delta
        if sample not in ignore_ids:
            if current_time >= adjusted_start and current_time < adjusted_end:
                stack = stacks[sample]
                root.add(stack, delta)
    return root
