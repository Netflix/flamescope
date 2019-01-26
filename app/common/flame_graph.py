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
import copy


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


def generate_flame_graph(nodes, samples, time_deltas, start_time, range_start, range_end, ignore_ids):
    root = Node('root')
    root_id = list(nodes.keys())[0] # assuming first item is root

    # no range defined, just return the callgraph
    if range_start is None and range_end is None:
        generate_callgraph(root, root_id, nodes, [])
        return root

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
        if ignore_ids is None or sample not in ignore_ids:
            if current_time >= range_start and current_time < range_end:
                stack = stacks[sample]
                root.add(stack, delta)
    return root
