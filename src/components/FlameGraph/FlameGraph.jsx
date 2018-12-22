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
import { Dimmer, Loader, Divider, Container, Button, Input, Dropdown } from 'semantic-ui-react'
import { pushBreadcrumb, popBreadcrumb } from '../../actions/Navbar'
import { connect } from 'react-redux'
import { flamegraph } from 'd3-flame-graph'
import { select } from 'd3-selection'
import 'd3-flame-graph/dist/d3-flamegraph.css'
import './flamegraph.less'
import queryString from 'query-string'
import { layout } from '../../config.jsx'

const styles = {
    container: {
        marginTop: '75px',
    },
    details: {
        fontSize: '14px',
        fontWeight: 300,
        minHeight: '5em',
    },
    layoutDropdown: {
        marginRight: 3.25,
    },
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
            'updateSearchQuery',
            'handleLayoutChange',
        ].forEach((k) => {
          this[k] = this[k].bind(this);
        });

        const preferredLayout = () => {
            if(localStorage.getItem('layout')){
                return localStorage.getItem('layout');
            } else return layout.flame;
        }
    
        this.state = {
          data: {},
          loading: false,
          chart: null,
          searchTerm: '',
          layout: preferredLayout()
        };
    }

    UNSAFE_componentWillMount() {
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
        fetch('/flamegraph/?filename=' + filename + '&start=' + start + '&end=' + end)
            .then(res => {
                return res.json()
            })
            .then(data => {
                this.setState({data: data, loading: false})
            })
            .then( () => {
                this.drawFlamegraph()
            })
            .then( () => {
                const query = queryString.parse(this.props.location.search);
                const sq = query["search"];
                if (sq) {
                    this.setState({searchTerm: sq});
                    this.state.chart.search(sq);
                }
            })

    }

    componentWillUnmount() {
        const { filename, start, end } = this.props.match.params
        this.props.popBreadcrumb('flamegraph_' + filename + '_' + start + '_' + end)
        this.props.popBreadcrumb('f_heatmap_' + filename)
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.location.search !== this.props.location.search) {
            const query = queryString.parse(nextProps.location.search);
            const sq = query['search'];
            if (sq) {
                this.setState({searchTerm: sq});
                this.state.chart.search(sq);
            } else {
                this.setState({searchTerm: ''});
                this.state.chart.clear()
            }
        }
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
            .minFrameSize(5)
            .inverted(this.state.layout === layout.icicle)

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
        this.updateSearchQuery('');
    }

    handleSearchInputChange(event, data) {
        this.setState({searchTerm: data.value})
    }

    handleSearchClick() {
        this.updateSearchQuery(this.state.searchTerm);
    }

    handleOnKeyDown(event) {
        if (event.which == 13) {
            this.updateSearchQuery(this.state.searchTerm);
        }
    }

    updateSearchQuery(nextQuery) {
        const params = new URLSearchParams(this.props.location.search);
        if (nextQuery === '') {
            params.delete('search');
        } else {
            params.set('search', nextQuery);
        }
        this.props.history.push({search: params.toString(),});
    }

    handleLayoutChange(event, data) {
        this.setState({layout: data.value}, () => {
            this.state.chart
                .inverted(this.state.layout === layout.icicle)
                .resetZoom()
            localStorage.setItem('layout', this.state.layout)
        })
    }

    render() {
        const searchButton = 
        <Button inverted color='red' size='small' onClick={this.handleSearchClick}>
            <Button.Content>Search</Button.Content>
        </Button>
        const layoutOptions = [
            {
                text: "Flame",
                value: layout.flame
            },
            {
                text: "Icicle",
                value: layout.icicle
            }
        ]

        return (
            <div>
                <Dimmer page inverted active={this.state.loading}>
                    <Loader size='huge' inverted>Loading</Loader>
                </Dimmer> 
                <Container style={styles.container}>
                    <Container textAlign='right'>
                        <Dropdown selection style={styles.layoutDropdown} options={layoutOptions} onChange={this.handleLayoutChange} defaultValue={this.state.layout} compact />
                        <Button size='small' onClick={this.handleResetClick}>
                            <Button.Content>
                                Reset Zoom
                            </Button.Content>
                        </Button>
                        <Button size='small' onClick={this.handleClearClick}>
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
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired,
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
