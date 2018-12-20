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

from app.common.perfutil import perf_read_offsets
from app.common.fileutil import get_profile_type
from app.common.error import InvalidFileError

def read_offsets(file_path):
    (profile_type, parsed_profile) = get_profile_type(file_path)
    if profile_type == 'perf_script':
        return perf_read_offsets(file_path)
    elif profile_type == 'trace_event':
        # TODO: process trace_event file.
        raise InvalidFileError('Unknown file type.')
    else:
        raise InvalidFileError('Unknown file type.')
