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

from os import walk
from os.path import join

from app import config
from app.common.fileutil import get_profile_type


# get profile files
def get_profile_list():
    all_files = []
    for root, dirs, files in walk(join(config.PROFILE_DIR)):
        start = root[len(config.PROFILE_DIR) + 1:]
        for f in files:
            if not f.startswith('.'):
                filename = join(start, f)
                file_path = join(config.PROFILE_DIR, filename)
                file_type = get_profile_type(file_path)
                all_files.append({
                    'filename': filename,
                    'type': file_type
                })

    return all_files
