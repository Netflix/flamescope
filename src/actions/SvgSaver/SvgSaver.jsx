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
export function exportGraph() {
    // Need to set styles inline, or they won't be picked up by the SVG.
    var labelElements = document.getElementsByClassName('d3-flame-graph-label')
    var i = 0
    for (i = 0; i < labelElements.length; i++) {
    labelElements[i].style.cssText = window.getComputedStyle(labelElements[i], null).cssText
    }

    var rectElements = document.getElementsByTagName('rect')
    i = 0
    for (i = 0; i < rectElements.length; i++) {
    rectElements[i].style.cssText = window.getComputedStyle(rectElements[i], null).cssText
    }

    var svg = document.getElementsByTagName('svg')[0]
    var source = new XMLSerializer().serializeToString(svg)

    if(!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)){
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"')
    }
    if(!source.match(/^<svg[^>]+"http:\/\/www\.w3\.org\/1999\/xlink"/)){
    source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
    }

    var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent('<?xml version="1.0" standalone="no"?>\r\n' + source)
    var link = document.getElementById("output_svg")
    link.href = url
    link.download = 'FlameGraph.svg'
    link.click()
}
