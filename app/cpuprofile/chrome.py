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


def get_cpuprofiles(chrome_profile):
    profile_events = []
    open_chunked_profile = None

    if "nodes" in chrome_profile:
        return [chrome_profile]

    for row in chrome_profile:
        if row['ph'] == 'I' and row['name'] == 'CpuProfile':
            # older chrome profiles
            profile_events.append(row['args']['data']['cpuProfile'])
        elif row['ph'] == 'P' and row['name'] == 'Profile':
            if open_chunked_profile is not None:
                profile_events.append(open_chunked_profile)
            open_chunked_profile = {
                'nodes': [],
                'samples': [],
                'timeDeltas': [],
                'startTime': row['args']['data']['startTime']
            }
        elif row['ph'] == 'P' and row['name'] == 'ProfileChunk':
            if 'nodes' in row['args']['data']['cpuProfile']:
                open_chunked_profile['nodes'].extend(row['args']['data']['cpuProfile']['nodes'])
            open_chunked_profile['samples'].extend(row['args']['data']['cpuProfile']['samples'])
            open_chunked_profile['timeDeltas'].extend(row['args']['data']['timeDeltas'])

    if open_chunked_profile is not None:
        profile_events.append(open_chunked_profile)

    return profile_events
