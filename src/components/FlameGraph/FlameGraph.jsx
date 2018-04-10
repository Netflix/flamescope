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
import { Dimmer, Loader, Divider, Container, Button, Input } from 'semantic-ui-react'
import { pushBreadcrumb, popBreadcrumb } from '../../actions/Navbar'
import { connect } from 'react-redux'
import { flamegraph } from 'd3-flame-graph'
import { select } from 'd3-selection'
import 'd3-flame-graph/dist/d3-flamegraph.css'
import './flamegraph.less'

const styles = {
    container: {
        marginTop: '75px',
    },
    details: {
        fontSize: '14px',
        fontWeight: 300,
        minHeight: '5em',
    }
}

class FlameGraph extends Component {
    constructor(props) {
        super(props);
    
        [
            'drawFlamegraph',
            'handleResetClick',
            'handleClearClick',
            'handleSearchInputChange',
            'handleSearchClick',
            'handleOnKeyDown',
        ].forEach((k) => {
          this[k] = this[k].bind(this);
        });
    
        this.state = {
          data: {},
          loading: false,
          chart: null,
          searchTerm: '',
        };
    }

    componentWillMount() {
        const { filename, start, end } = this.props.match.params
        this.props.pushBreadcrumb('f_heatmap_' + filename, 'Heatmap (' + filename + ')', '/#/heatmap/' + filename)
        this.props.pushBreadcrumb(
            'flamegraph_' + filename + '_' + start + '_' + end, 
            'Flame Graph (' + start + ', ' + end + ')', 
            '/#/heatmap/' + filename + '/flamegraph/' + start + '/' + end
        )
    }

    componentDidMount() {
        const { filename, start, end } = this.props.match.params

        this.setState({loading: true})
        fetch('/stack/?filename=' + filename + '&start=' + start + '&end=' + end)
            .then(res => {
                return res.json()
            })
            .then(data => {
                this.setState({data: data, loading: false})
            })
            .then( () => {
                this.drawFlamegraph()
            })
    }

    componentWillUnmount() {
        const { filename, start, end } = this.props.match.params
        this.props.popBreadcrumb('flamegraph_' + filename + '_' + start + '_' + end)
        this.props.popBreadcrumb('f_heatmap_' + filename)
    }

    drawFlamegraph() {
        const { data } = this.state;
        const width = document.getElementById('flamegraph').offsetWidth

        const cellHeight = 16
        const chart = flamegraph()
            .width(width)
            .cellHeight(cellHeight)
            .transitionDuration(750)
            .sort(true)
            .title('')

        var details = document.getElementById("details")
        chart.details(details)

        select(`#flamegraph`)
            .datum(data)
            .call(chart)

        this.setState({chart: chart})
    }

    handleResetClick() {
        this.state.chart.resetZoom()
    }

    handleClearClick() {
        this.setState({searchTerm: ''})
        this.state.chart.clear()
    }

    handleSearchInputChange(event, data) {
        this.setState({searchTerm: data.value})
    }

    handleSearchClick() {
        this.state.chart.search(this.state.searchTerm)
    }

    handleOnKeyDown(event) {
        if (event.which == 13) {
            this.state.chart.search(this.state.searchTerm)
        }
    }

    render() {
        const searchButton = 
        <Button color='red' size='small' onClick={this.handleSearchClick}>
            <Button.Content>Search</Button.Content>
        </Button>
        
        return (
            <div>
                <Dimmer page inverted active={this.state.loading}>
                    <Loader size='huge' inverted>Loading</Loader>
                </Dimmer> 
                <Container style={styles.container}>
                    <Container textAlign='right'>
                        <Button inverted color='red' size='small' onClick={this.handleResetClick}>
                            <Button.Content>
                                Reset Zoom
                            </Button.Content>
                        </Button>
                        <Button inverted color='red' size='small' onClick={this.handleClearClick}>
                            <Button.Content>
                                Clear
                            </Button.Content>
                        </Button>
                        <Input
                            action={searchButton}
                            placeholder='Search...'
                            value={this.state.searchTerm}
                            onChange={this.handleSearchInputChange}
                            onKeyDown={this.handleOnKeyDown}
                        />
                    </Container>
                    <Divider />
                    <div
                        ref={`flamegraph`}
                        id={`flamegraph`}
                        key={`flamegraph`}
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

FlameGraph.propTypes = {
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
)(FlameGraph)