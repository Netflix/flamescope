import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Dimmer, Loader, Divider } from 'semantic-ui-react'
import { pushBreadcrumb, popBreadcrumb } from '../../actions/Navbar'
import { connect } from 'react-redux'
import { flamegraph } from 'd3-flame-graph'
import { select } from 'd3-selection'
import 'd3-flame-graph/dist/d3-flamegraph.css'

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
    
        ['drawFlamegraph'].forEach((k) => {
          this[k] = this[k].bind(this);
        });
    
        this.state = {
          data: {},
          loading: false,
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
        fetch('/stack?filename=' + filename + '&start=' + start + '&end=' + end)
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

        const cellHeight = 22;
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
    }

    render() {
        
        return (
            <div style={styles.container}>
                <Dimmer page inverted active={this.state.loading}>
                    <Loader size='huge' inverted>Loading</Loader>
                </Dimmer> 
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