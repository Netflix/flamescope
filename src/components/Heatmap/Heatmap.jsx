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

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Dimmer, Loader, Divider, Button, Container, Modal, Dropdown, Label, Checkbox, Grid, Icon } from 'semantic-ui-react'
import { connect } from 'react-redux'
import { select } from 'd3-selection'
import { scaleLinear } from 'd3-scale'
import { heatmap } from 'd3-heatmap2'
import queryString from 'query-string'
import 'd3-heatmap2/dist/d3-heatmap2.css'
import './heatmap.less'
import checkStatus from '../../common/CheckStatus'

const styles = {
    container: {
        marginTop: '75px',
    },
    details: {
        fontSize: '14px',
        fontWeight: 300,
        minHeight: '5em',
    },
    enhanceToggle: {
        top: '4px',
    },
    enhanceLabel: {
        marginLeft: '8px',
    }
}

const rowsOptions = [
    { key: 10, text: '10', value: '10' },
    { key: 25, text: '25', value: '25' },
    { key: 49, text: '49', value: '49' },
    { key: 50, text: '50', value: '50' },
    { key: 99, text: '99', value: '99' },
    { key: 100, text: '100', value: '100' },
]

const heatmapColors = {
  default:  ['#FFFFFF', '#FF5032', '#E50914'],
  enhanced: ['#FFFFFF', '#6AAAFF', '#FAA0B5', '#FF5032', '#E50914']
}

class Heatmap extends Component {
    constructor(props) {
        super(props);

        [
            'drawHeatmap',
            'handleSettingsClose',
            'handleSettingsOpen',
            'handleApply',
            'handleEnhanceColors',
            'handleRowsChange',
            'fetchData',
            'handleBackClick',
            'handleFullProfileClick',
        ].forEach((k) => {
          this[k] = this[k].bind(this);
        });

        this.state = {
          data: {},
          rows: '50',
          loading: false,
          settingsOpen: false,
          enhanceColors: false
        };
    }

    componentDidMount() {
        this.fetchData()
    }

    fetchData() {
        const { filename, type } = this.props.match.params
        const { rows } = this.state

        this.setState({loading: true})
        fetch(`/heatmap/?filename=${filename}&type=${type}&rows=${rows}`)
            .then(checkStatus)
            .then(res => {
                return res.json()
            })
            .then(data => {
                this.setState({data: data, loading: false})
            })
            .then( () => {
                this.drawHeatmap()
            })
            .catch((error) => {
                error.response.json()
                    .then( json => {
                        this.props.history.push(`/error/${error.code}?${queryString.stringify({message: json.error})}`)
                    })
                    .catch(() => {
                        this.props.history.push(`/error/${error.code}?${queryString.stringify({message: error.message})}`)
                    })
            })
    }

    drawHeatmap() {
        const self = this
        const { data , enhanceColors} = this.state;
        const { filename, type, compareType, compareFilename, compareStart, compareEnd } = this.props.match.params

        const heatmapNode = document.getElementById('heatmap')
        while (heatmapNode.firstChild) {
            heatmapNode.removeChild(heatmapNode.firstChild)
        }

        const legendNode = document.getElementById('legend')
        while (legendNode.firstChild) {
            legendNode.removeChild(legendNode.firstChild)
        }

        var width = heatmapNode.offsetWidth

        var gridSize = width / data.columns.length

        if (gridSize > 10) {
            width = data.columns.length * 10
        } else if (gridSize < 6) {
            width = data.columns.length * 6
        }

        var ticks = Math.floor(width / 50)

        var legendWidth = Math.min(width * 0.8, 400)
        var legendTicks = legendWidth > 100 ? Math.floor(legendWidth / 50) : 2

        function onClick(d, i, j) {
            rangeSelect([i, j])
        }

        function onMouseOver(d, i, j) {
            document.getElementById("details").innerHTML = "second: " + data.columns[i] + ", millisecond: " + data.rows[j] + ", count: " + d
            hover([i, j])
        }

        const chart = heatmap()
            .title("")
            .subtitle("")
            .legendLabel("Count")
            .legendScaleTicks(legendTicks)
            .width(width)
            .xAxisScale([data.columns[0], data.columns[data.columns.length - 1]])
            .xAxisScaleTicks(ticks)
            .highlightColor('#936EB5')
            .highlightOpacity('0.4')
            .gridStrokeOpacity(0.0)
            .invertHighlightRows(true)
            .onClick(onClick)
            .onMouseOver(onMouseOver)
            .colorScale(scaleLinear()
                .domain( enhanceColors ? [0, 1, 3, data.maxvalue/2, data.maxvalue] : [0, data.maxvalue/2 , data.maxvalue])
                .range( enhanceColors ? heatmapColors.enhanced : heatmapColors.default)
            )
            .margin({
                top: 40,
                right: 0,
                bottom: 10,
                left: 3
            })
            .legendElement("#legend")
            .legendHeight(50)
            .legendWidth(300)
            .legendMargin({top: 0, right: 0, bottom: 30, left: 0})

        function heatmap2time(cell, end = false) {
            var secs = data.columns[cell[0]]
            var millisDelta = end ? data.rows[0] - data.rows[1] : 0.0
            var millis = data.rows[cell[1]] + millisDelta
            return secs + ( millis / 1000 )
        }

        let selectStart = null
        let selectEnd = null

        function rangeSelect(cell) {
            if (!selectStart) {
              selectStart = cell
              chart.setHighlight([{"start": selectStart, "end": selectStart}])
              chart.updateHighlight()
            } else if (!selectEnd) {
                if (isBefore(selectStart, cell)) {
                    selectEnd = cell
                } else {
                    selectEnd = selectStart
                    selectStart = cell
                }
                chart.setHighlight([{"start": selectStart, "end": selectEnd}])
                chart.updateHighlight()

                let url = `/flamegraph/${type}/${filename}/${heatmap2time(selectStart)}/${heatmap2time(selectEnd, true)}`

                if (compareType && compareFilename) {
                    url = `/differential/${compareType}/${compareFilename}`
                    if (compareStart && compareEnd) {
                        url += `/${compareStart}/${compareEnd}`
                    }
                    url += `/compare/${type}/${filename}/${heatmap2time(selectStart)}/${heatmap2time(selectEnd, true)}`
                }

                self.props.history.push(url)
            } else {
              selectStart = cell
              selectEnd = null
              chart.setHighlight([{"start": selectStart, "end": selectStart}])
              chart.updateHighlight()
            }
        }

        function hover(cell) {
          if (selectStart && !selectEnd) {
            if (isBefore(selectStart, cell)) {
              chart.setHighlight([{"start": selectStart, "end": cell}])
            } else {
              chart.setHighlight([{"start": cell, "end": selectStart}])
            }
            chart.updateHighlight()
          }
        }

        /**
         * Returns true if cellA is before cellB in our time domain.
         */
        function isBefore(cellA, cellB) {
            if (cellA[0] < cellB[0]) {
              return true
            }
            return cellA[0] == cellB[0] && cellA[1] > cellB[1]
        }

        select("#heatmap")
            .datum(data.values)
            .call(chart)

        // click outside of the heatmap
        document.documentElement.addEventListener('click', function (element) {
            if (element.target.nodeName !== 'rect') {
                selectStart = null
                selectEnd = null
                chart.setHighlight([])
                chart.updateHighlight()
            }
        })

        // press escape key
        window.addEventListener('keydown', function (event) {
            if (event.defaultPrevented) {
              return // do nothing if the event was already processed
            }

            if (event.key === 'Escape') {
                selectStart = null
                selectEnd = null
                chart.setHighlight([])
                chart.updateHighlight()
            }
        })
    }

    handleSettingsOpen() {
        this.setState({settingsOpen: true})
    }

    handleSettingsClose() {
        this.setState({settingsOpen: false})
    }

    handleApply() {
        this.setState(
            {settingsOpen: false},
            function() {
                this.fetchData()
            }
        )
    }

    handleRowsChange(event, data) {
        if (data.value !== this.state.rows) {
            this.setState(
                {rows: data.value},
                function() {
                    this.fetchData()
                }
            )
        }
    }

    handleEnhanceColors(){
        this.setState(
            {enhanceColors: !this.state.enhanceColors},
            function() {
                this.drawHeatmap()
            }
        )
    }

    handleBackClick() {
        this.props.history.goBack();
    }

    handleFullProfileClick() {
        const { filename, type, compareType, compareFilename, compareStart, compareEnd } = this.props.match.params

        let url = `/flamegraph/${type}/${filename}`

        if (compareType && compareFilename) {
            url = `/differential/${compareType}/${compareFilename}`
            if (compareStart && compareEnd) {
                url += `/${compareStart}/${compareEnd}`
            }
            url += `/compare/${type}/${filename}`
        }

        this.props.history.push(url)
    }

    render() {
        return (
            <div>
                <Dimmer page inverted active={this.state.loading}>
                    <Loader size='huge' inverted>Loading</Loader>
                </Dimmer>
                <Modal
                    size='tiny'
                    open={this.state.settingsOpen}
                    onClose={this.handleSettingsClose}
                    closeIcon={false}
                >
                    <Modal.Header>
                        Heatmap Settings
                    </Modal.Header>
                    <Modal.Content>
                        <p>Modal Settings</p>
                    </Modal.Content>
                    <Modal.Actions>
                        <Button onClick={this.handleApply}>
                            Apply
                        </Button>
                    </Modal.Actions>
                </Modal>
                <Container style={styles.container}>
                    <Grid>
                        <Grid.Column width={4}>
                            <Button content='Back' icon='left arrow' onClick={this.handleBackClick} />
                        </Grid.Column>
                        <Grid.Column width={12} textAlign='right'>
                            <Label pointing='right' color='red' size='large'>
                                Rows
                            </Label>
                            <Dropdown
                                options={rowsOptions}
                                onChange={this.handleRowsChange}
                                value={this.state.rows}
                                compact
                                selection
                                labeled
                            />
                            {/*<Button animated='vertical' color='red' onClick={this.handleSettingsOpen}>
                                <Button.Content hidden>Settings</Button.Content>
                                <Button.Content visible>
                                    <Icon name='cogs' />
                                </Button.Content>
                            </Button>*/}
                            <Label pointing='right' color='red' size='large' style={styles.enhanceLabel}>
                                Enhanced
                            </Label>
                            <Checkbox
                                toggle
                                checked={this.state.enhanceColors}
                                onClick={this.handleEnhanceColors}
                                style={styles.enhanceToggle}
                            />
                        </Grid.Column>
                    </Grid>
                    <Divider />
                    <div
                        ref={`heatmap`}
                        id={`heatmap`}
                        key={`heatmap`}
                        className={`heatmap`}
                    />
                    <div
                        ref={`legend`}
                        id={`legend`}
                        key={`legend`}
                        className={`legend`}
                    />
                    <Divider />
                    <Grid>
                        <Grid.Column width={12}>
                            <div
                                ref={`details`}
                                id={`details`}
                                key={`details`}
                                style={styles.details}
                            />
                        </Grid.Column>
                        <Grid.Column width={4} textAlign='right'>
                            <Button icon labelPosition='right' onClick={this.handleFullProfileClick}>
                                Whole Profile
                                <Icon name='right arrow' />
                            </Button>
                        </Grid.Column>
                    </Grid>
                </Container>
            </div>
        )
    }
}

Heatmap.propTypes = {
    match: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired,
}

const mapStateToProps = () => {
    return {
    }
}

const mapDispatchToProps = () => {
    return {
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(Heatmap)
