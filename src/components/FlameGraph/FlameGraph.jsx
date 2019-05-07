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
import { Dimmer, Loader, Divider, Container, Button, Input, Dropdown, Grid, Checkbox, Icon } from 'semantic-ui-react'
import { connect } from 'react-redux'
import { flamegraph } from 'd3-flame-graph'
import { select } from 'd3-selection'
import 'd3-flame-graph/dist/d3-flamegraph.css'
import './flamegraph.less'
import queryString from 'query-string'
import { layout } from '../../config.jsx'
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
    layoutDropdown: {
        marginRight: 3.25,
    },
    packageNameToggle: {
        marginRight: 5,
    },
}

class FlameGraph extends Component {
    constructor(props) {
        super(props);
    
        [
            'drawFlamegraph',
            'executeQuery',
            'handleResetClick',
            'handleClearClick',
            'handleSearchInputChange',
            'handleSearchClick',
            'handleOnKeyDown',
            'updateSearchQuery',
            'handleLayoutChange',
            'handleBackClick',
            'handlePackageNameClick',
            'handleCompareClick',
            'handleFlipClick',
            'handleElidedDifferentialFlipClick',
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
          layout: preferredLayout(),
          packageName: false,
        };
    }

    componentDidMount() {
        this.executeQuery()
    }

    componentDidUpdate(prevProps) {
        if (
            this.props.location.search !== prevProps.location.search || 
            this.props.match.params !== prevProps.match.params ||
            this.props.compare !== prevProps.compare
        ) {
            select('#flamegraph').selectAll('svg').remove()
            this.executeQuery()
        }
    }

    executeQuery() {
        const { type, filename, start, end, compareType, compareFilename, compareStart, compareEnd } = this.props.match.params
        const { compare } = this.props
        const { packageName } = this.state

        let url = `/flamegraph/?filename=${filename}&type=${type}&packageName=${packageName ? 'true' : 'false'}`

        if (compare == 'differential') {
            url = `/differential/?filename=${filename}&type=${type}&compareFilename=${compareFilename}&compareType=${compareType}`
        } else if (compare == 'elided') {
            url = `/elided/?filename=${filename}&type=${type}&compareFilename=${compareFilename}&compareType=${compareType}`
        }

        if (start && end) {
            url += `&start=${start}&end=${end}`
        }

        if (compareStart && compareEnd) {
            url += `&compareStart=${compareStart}&compareEnd=${compareEnd}`
        }

        this.setState({loading: true})

        fetch(url)
            .then(checkStatus)
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
                } else {
                    this.setState({searchTerm: ''});
                    this.state.chart.clear()
                }    
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

    drawFlamegraph() {
        const { data } = this.state
        const { compare } = this.props
        const width = document.getElementById('flamegraph').offsetWidth

        const cellHeight = 16
        const chart = flamegraph()
            .width(width)
            .cellHeight(cellHeight)
            .transitionDuration(750)
            .sort(true)
            .title('')
            .differential(compare === 'differential' ? true : false)
            .minFrameSize(5)
            .inverted(this.state.layout === layout.icicle)
            .selfValue(true)

        var details = document.getElementById("details")
        chart.details(details)

        select(`#flamegraph`)
            .datum(data)
            .call(chart)

        this.setState({chart: chart})
    }

    handlePackageNameClick() {
        this.setState({packageName: !this.state.packageName}, () => {
            this.executeQuery()
        })
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

    handleBackClick() {
        this.props.history.goBack();
    }

    handleCompareClick() {
        const { type, filename, start, end } = this.props.match.params

        let url = `/#/compare/${type}/${filename}`

        if (start && end) {
            url += `/${start}/${end}`
        }

        window.location.href = url
    }

    handleFlipClick() {
        const { type, filename, start, end, compareType, compareFilename, compareStart, compareEnd } = this.props.match.params
        const { compare } = this.props

        let url = `/${compare}/${compareType}/${compareFilename}`
        if (compareStart && compareEnd) {
            url += `/${compareStart}/${compareEnd}`
        }
        url += `/compare/${type}/${filename}`
        if (start && end) {
            url += `/${start}/${end}`
        }
        
        this.props.history.push(url)
    }


    handleElidedDifferentialFlipClick() {
        const { type, filename, start, end, compareType, compareFilename, compareStart, compareEnd } = this.props.match.params
        const { compare } = this.props

        let url = `/${compare === 'differential' ? 'elided' : 'differential'}/${type}/${filename}`
        if (start && end) {
            url += `/${start}/${end}`
        }
        url += `/compare/${compareType}/${compareFilename}`
        if (compareStart && compareEnd) {
            url += `/${compareStart}/${compareEnd}`
        }
        
        this.props.history.push(url)
    }

    render() {
        const { type } = this.props.match.params
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
                    <Grid>
                        <Grid.Column width={4}>
                            <Button content='Back' icon='left arrow' onClick={this.handleBackClick} />
                        </Grid.Column>
                        <Grid.Column width={12} textAlign='right'>
                            { type == 'nflxprofile' || type == 'cpuprofile' ?
                                <Checkbox
                                    toggle
                                    checked={this.state.packageName}
                                    onClick={this.handlePackageNameClick}
                                    label='Java Package Name'
                                    style={styles.packageNameToggle}
                                />
                            : null }
                            { this.props.compare ?
                                <Button inverted color='red' size='small' onClick={this.handleFlipClick}>
                                    <Button.Content>
                                        Flip
                                    </Button.Content>
                                </Button>
                            : null }
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
                        </Grid.Column>
                    </Grid>
                    <Divider />
                    <div
                        ref={`flamegraph`}
                        id={`flamegraph`}
                        key={`flamegraph`}
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
                            { !this.props.compare ?
                            <Button icon labelPosition='right' onClick={this.handleCompareClick}>
                                Compare
                                <Icon name='right arrow' />
                            </Button>
                            : this.props.compare === 'differential' ?
                            <Button icon labelPosition='right' onClick={this.handleElidedDifferentialFlipClick}>
                                View Elided Frames
                                <Icon name='right arrow' />
                            </Button> :
                            <Button icon labelPosition='right' onClick={this.handleElidedDifferentialFlipClick}>
                                View Differential
                                <Icon name='right arrow' />
                            </Button> }
                        </Grid.Column>
                    </Grid>
                </Container>
            </div>
        )
    }
}

FlameGraph.propTypes = {
    compare: PropTypes.string,
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired,
    match: PropTypes.object.isRequired,
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
)(FlameGraph)
