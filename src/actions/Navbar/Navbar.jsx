/**
 *
 *  Copyright 2018 Netflix, Inc.
 *
 *     Licensed under the Apache License, Version 2.0 (the "License");
 *     you may not use this file except in compliance with the License.
 *     You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 *     Unless required by applicable law or agreed to in writing, software
 *     distributed under the License is distributed on an "AS IS" BASIS,
 *     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *     See the License for the specific language governing permissions and
 *     limitations under the License.
 *
 */

export const PUSH_BREADCRUMB = 'PUSH_BREADCRUMB'
export const POP_BREADCRUMB = 'POP_BREADCRUMB'

export function pushBreadcrumb(key, content, href) {
    return {
        type: PUSH_BREADCRUMB,
        key: key,
        content: content,
        href: href,
    }
}

export function popBreadcrumb(key) {
    return {
        type: POP_BREADCRUMB,
        key: key,
    }
}