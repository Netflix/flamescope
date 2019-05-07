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


# TODO: including parent in the nodes will remove the need for stack generation
def _get_regular_stacks(nflxprofile_nodes, root_node_id):
    stacks = {}
    queue = []
    queue.append((root_node_id, None))

    while queue:
        (nflxprofile_node_id, parent_node_id) = queue.pop(0)
        nflxprofile_node = nflxprofile_nodes[nflxprofile_node_id]
        if not parent_node_id:
            stacks[nflxprofile_node_id] = [
                (nflxprofile_node.function_name, nflxprofile_node.libtype)
            ]
        else:
            stacks[nflxprofile_node_id] = stacks[parent_node_id] + \
                [(nflxprofile_node.function_name, nflxprofile_node.libtype)]
        for child_id in nflxprofile_node.children:
            queue.append((child_id, nflxprofile_node_id))

    return stacks


def _get_package_name_stacks(nflxprofile_nodes):
    stacks = {}
    for key in nflxprofile_nodes:
        nflxprofile_node = nflxprofile_nodes[key]
        function_name = nflxprofile_node.function_name.split(';')[0]
        function_name_arr = function_name.split('/')
        stack_arr = []
        for package_name in function_name_arr:
            stack_arr.append((package_name, nflxprofile_node.libtype))
        stacks[key] = stack_arr

    return stacks


def _get_stacks(nflxprofile_nodes, root_node_id, package_name=False):
    if package_name:
        return _get_package_name_stacks(nflxprofile_nodes)
    return _get_regular_stacks(nflxprofile_nodes, root_node_id)


def _get_child(node, name, libtype):
    for child in node['c']:
        if child['n'] == name and child['l'] == libtype:
            return child
    return None


def generate_flame_graph(profiles, root_ids, ignore_ids, range_start, range_end, package_name=False):
    """Docstring for public method."""
    root = {
        'n': 'root',
        'l': '',
        'v': 0,
        'c': []
    }

    for profile_index, profile in enumerate(profiles):
        if isinstance(profile, dict):
            nodes = profile['nodes']
            samples = profile['samples']
            time_deltas = profile['timeDeltas']
            start_time = profile['startTime']
        else:
            nodes = profile.nodes
            samples = profile.samples
            time_deltas = profile.time_deltas
            start_time = profile.start_time

        root_id = root_ids[profile_index]
        ignore_id = ignore_ids[profile_index]

        current_time = start_time + time_deltas[0]
        stacks = _get_stacks(nodes, root_id, package_name)
        for sample_index, sample in enumerate(samples):
            if sample_index == (len(samples) - 1):  # last sample
                break
            delta = time_deltas[sample_index + 1]
            current_time += delta
            if not ignore_id or sample not in ignore_id:
                if (range_start is None or range_end is None) or (range_start <= current_time < range_end):
                    stack = stacks[sample]
                    current_node = root
                    for frame in stack:
                        child = _get_child(current_node, frame[0], frame[1])
                        if child is None:
                            child = {
                                'n': frame[0],
                                'l': frame[1],
                                'v': 0,
                                'c': []
                            }
                            current_node['c'].append(child)
                        current_node = child
                    current_node['v'] = current_node['v'] + 1
    return root


def _apply_weight(node, weight):
    queue = []
    queue.append(node)
    while queue:
        current_node = queue.pop(0)
        current_node['v'] = int(round(current_node['v'] * weight))
        for child in current_node['c']:
            queue.append(child)


def _get_full_value(flame_graph):
    full_value = 0
    queue = []
    queue.append(flame_graph)
    while queue:
        node = queue.pop(0)
        full_value += node['v']
        for child in node['c']:
            queue.append(child)
    return full_value


def get_differential_flame_graph(flame_graph_1, flame_graph_2):
    """Docstring for public method."""
    full_value_1 = _get_full_value(flame_graph_1)
    full_value_2 = _get_full_value(flame_graph_2)

    weight = full_value_1 / full_value_2

    queue = []
    queue.append((flame_graph_1, flame_graph_2))
    while queue:
        (node_1, node_2) = queue.pop(0)
        if node_2 is not None:
            node_1['d'] = int(round(node_1['v'] - (node_2['v'] * weight)))
            for child_1 in node_1['c']:
                child_2 = _get_child(node_2, child_1['n'], child_1['l'])
                queue.append((child_1, child_2))
        else:
            node_1['d'] = node_1['v']

    return flame_graph_1


def get_elided_flame_graph(flame_graph_1, flame_graph_2):
    """Docstring for public method."""
    full_value_1 = _get_full_value(flame_graph_1)
    full_value_2 = _get_full_value(flame_graph_2)

    weight = full_value_1 / full_value_2

    queue = []
    queue.append((flame_graph_1, flame_graph_2))
    while queue:
        (node_1, node_2) = queue.pop(0)
        if node_1 is None:
            # it's an elided frame
            _apply_weight(node_2, weight)
        else:
            # it's not an elided frame
            node_2['v'] = 0
            for child_2 in node_2['c']:
                child_1 = _get_child(node_1, child_2['n'], child_2['l'])
                queue.append((child_1, child_2))

    return flame_graph_2
