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


def generate_callgraph(root, node_id, nodes, stack):
    node = nodes[node_id]  # break in case id doesn't exist
    if node['function_name'] != '(idle)':
        if node['function_name'] == '':
            node['function_name'] = '(anonymous)'
        stack.append(node['function_name'])
        if node['hit_count'] > 0:
            root.add(stack, node['hit_count'])
        if node['children']:
            for child in node['children']:
                generate_callgraph(root, child, nodes, copy.copy(stack))
    del nodes[node_id]


def cpuprofile_generate_flame_graph(filename, range_start, range_end, profile=None):
    if not profile:
        file_path = join(config.PROFILE_DIR, filename)
        f = get_file(file_path)
        profile = json.load(f)
        f.close()

    root = Node('root')
    root_id = profile['nodes'][0]['id']
    nodes = parse_nodes(profile)
    generate_callgraph(root, root_id, nodes, [])

    return root
