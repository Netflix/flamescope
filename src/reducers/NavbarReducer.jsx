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

import { PUSH_BREADCRUMB, POP_BREADCRUMB } from '../actions/Navbar/Navbar'

const initialNavbarState = {
    breadcrumbs: [
        { key: 'home', content: 'Home', href: '/#' },
    ]
}

function findCrumb(crumbs, key) {
  return crumbs.findIndex(function(element) {
    return element.key === key
  })
}

function sliceBreadcrumbs(crumbs, key) {
  var found = findCrumb(crumbs, key)
  if (found !== -1) {
    var first = []
    if (found > 0) {
      first = crumbs.slice(0, found)
    }
    var second = crumbs.slice(found +1)
    return first.concat(second)
  } else {
    return crumbs
  }
}

function pushCrumb(crumbs, key, content, href) {
  var found = findCrumb(crumbs, key)
  if (found < 0) {
    return [
      ...crumbs,
      {
        key: key,
        content: content,
        href: href,
      }
    ]
  } else {
    return crumbs
  }
}

function navbar(state = initialNavbarState, action) {
  switch (action.type) {
    case PUSH_BREADCRUMB:
      return Object.assign({}, state, {
        breadcrumbs: pushCrumb(state.breadcrumbs, action.key, action.content, action.href)
      })
    case POP_BREADCRUMB:
      return Object.assign({}, state, {
        breadcrumbs: sliceBreadcrumbs(state.breadcrumbs, action.key)
      })
    default:
      return state
  }
}

export default navbar