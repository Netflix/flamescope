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
def _get_stacks(nflxprofile_nodes, root_node_id):
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


def _get_child(node, name, libtype):
    for child in node['children']:
        if child['name'] == name and child['libtype'] == libtype:
            return child
    return None


def generate_flame_graph(profiles, root_ids, ignore_ids, range_start, range_end):
    """Docstring for public method."""
    root = {
        'name': 'root',
        'libtype': '',
        'value': 0,
        'children': []
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
        stacks = _get_stacks(nodes, root_id)
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
                                'name': frame[0],
                                'libtype': frame[1],
                                'value': 0,
                                'children': []
                            }
                            current_node['children'].append(child)
                        current_node = child
                    current_node['value'] = current_node['value'] + 1
    return root
