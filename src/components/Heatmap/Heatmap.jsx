import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Dimmer, Loader, Divider, Button, Container, Modal, Dropdown, Label } from 'semantic-ui-react'
import { pushBreadcrumb, popBreadcrumb } from '../../actions/Navbar'
import { connect } from 'react-redux'
import { select } from 'd3-selection'
import { scaleLinear } from 'd3-scale'
import { heatmap } from 'd3-heatmap2'
import 'd3-heatmap2/dist/d3-heatmap2.css'
import './heatmap.less'

const styles = {
    container: {
        marginTop: '75px',
    },
    details: {
        fontSize: '14px',
        fontWeight: 300,
        minHeight: '5em',
    },
}

const rowsOptions = [
    { key: 10, text: '10', value: '10' },
    { key: 25, text: '25', value: '25' },
    { key: 49, text: '49', value: '49' },
    { key: 50, text: '50', value: '50' },
    { key: 99, text: '99', value: '99' },
    { key: 100, text: '100', value: '100' },
]

class Heatmap extends Component {
    constructor(props) {
        super(props);
    
        [
            'drawHeatmap',
            'handleSettingsClose',
            'handleSettingsOpen',
            'handleApply',
            'handleRowsChange',
            'fetchData',
        ].forEach((k) => {
          this[k] = this[k].bind(this);
        });
    
        this.state = {
          data: {},
          rows: '50',
          loading: false,
          settingsOpen: false,
        };
    }

    componentWillMount() {
        const { filename } = this.props.match.params

        this.props.pushBreadcrumb('heatmap_' + filename, 'Heatmap (' + filename + ')', '/#/heatmap/' + filename)
    }

    componentDidMount() {
        this.fetchData()
    }

    componentWillUnmount() {
        const { filename } = this.props.match.params
        this.props.popBreadcrumb('heatmap_' + filename)
    }

    fetchData() {
        const { filename } = this.props.match.params
        const { rows } = this.state

        this.setState({loading: true})
        fetch('/heatmap/?filename=' + filename + '&rows=' + rows)
            .then(res => {
                return res.json()
            })
            .then(data => {
                this.setState({data: data, loading: false})
            })
            .then( () => {
                this.drawHeatmap()
            })
    }

    drawHeatmap() {
        const { data } = this.state;
        const { filename } = this.props.match.params

        const heatmapNode = document.getElementById('heatmap')
        while (heatmapNode.firstChild) {
            heatmapNode.removeChild(heatmapNode.firstChild)
        }

        var width = heatmapNode.offsetWidth

        document.getElementById('heatmap')

        var gridSize = width / data.columns.length

        if (gridSize > 10) {
            width = data.columns.length * 10
        } else if (gridSize < 6) {
            width = data.columns.length * 6
        }

        var ticks = Math.floor(width / 50)

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
                .domain([0, data.maxvalue / 2, data.maxvalue])
                .range(['#FFFFFF', '#FF5032', '#E50914'])
            )
            .margin({
                top: 40,
                right: 0,
                bottom: 10,
                left: 3
            })

        function heatmap2time(cell, end = false) {
            var secs = data.columns[cell[0]]
            var millisDelta = end ? data.rows[0] - data.rows[1] : 0.0
            var millis = data.rows[cell[1]] + millisDelta
            if (millis > 999) {
                var quotient = Math.floor(millis / 1000)
                var remainder = millis % 1000
                secs = secs + quotient
                millis = remainder
            }
            return secs + '.' + millis
        }
        
        let selectStart = null
        let selectEnd = null

        function rangeSelect(cell) {
            if (!selectStart) {
                selectStart = cell
                chart.setHighlight([{"start": selectStart, "end": selectStart}])
                chart.updateHighlight()
            } else if (!selectEnd) {
                selectEnd = cell
                chart.setHighlight([{"start": selectStart, "end": selectEnd}])
                chart.updateHighlight()
                window.location.href = `/#/heatmap/${filename}/flamegraph/${heatmap2time(selectStart)}/${heatmap2time(selectEnd, true)}/`;
            } else {
                selectStart = cell
                selectEnd = null
                chart.setHighlight([{"start": selectStart, "end": selectStart}])
                chart.updateHighlight()
            }
        }

        function hover(cell) {
			if (selectStart && !selectEnd) {
				if (cell[0] > selectStart[0]) { // column is higher
					chart.setHighlight([{"start": selectStart, "end": cell}])
					chart.updateHighlight()
				} else if (cell[0] == selectStart[0]) { // same column
                    if (cell[1] <= selectStart[1]) { // row is lower or equal
                        chart.setHighlight([{"start": selectStart, "end": cell}])
                        chart.updateHighlight()
                    } else {
                        chart.setHighlight([{"start": selectStart, "end": selectStart}])
                        chart.updateHighlight()
                    }
				} else {
					chart.setHighlight([{"start": selectStart, "end": selectStart}])
					chart.updateHighlight()
				}
			}
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
                    <Container textAlign='right'>
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
                        {/* <Button animated='vertical' color='red' onClick={this.handleSettingsOpen}>
                            <Button.Content hidden>Settings</Button.Content>
                            <Button.Content visible>
                                <Icon name='cogs' />
                            </Button.Content>
                        </Button> */}
                    </Container>
                    <Divider />
                    <div
                        ref={`heatmap`}
                        id={`heatmap`}
                        key={`heatmap`}
                        className={`heatmap`}
                    />
                    <Divider />
                    <div
                        ref={`details`}
                        id={`details`}
                        key={`details`}
                        style={styles.details}
                    />
                </Container>
            </div>
        )
    }
}

Heatmap.propTypes = {
    match: PropTypes.object.isRequired,
    popBreadcrumb: PropTypes.func.isRequired,
    pushBreadcrumb: PropTypes.func.isRequired,
}

const mapStateToProps = () => {
    return {
    }
}

const mapDispatchToProps = dispatch => {
    return {
        pushBreadcrumb: (key, content, href) => {
            dispatch(pushBreadcrumb(key, content, href))
        },
        popBreadcrumb: key => {
            dispatch(popBreadcrumb(key))
        }
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(Heatmap)
