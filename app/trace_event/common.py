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

from cachetools import cached, LRUCache
from cachetools.keys import hashkey


@cached(cache=LRUCache(maxsize=256), key=lambda file_path, mtime, profile: hashkey(file_path, mtime))
def get_time_range(file_path, mtime, profile):
    start_time = None
    end_time = None

    for row in profile:
        if row['ph'] != 'M':
            start_time = row['ts']
            break

    for row in reversed(profile):
        if row['ph'] != 'M':
            end_time = row['ts']
            break

    return (start_time, end_time)
