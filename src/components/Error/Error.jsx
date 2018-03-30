import React, { Component } from 'react'
import { Header } from 'semantic-ui-react'
import PropTypes from 'prop-types'

const styles = {
    header: {
        marginTop: '75px',
    }
}

class Error extends Component {
    render() {
        const { code } = this.props.match.params
        return (
            <Header style={styles.header}>{code}</Header>
        )
    }
}

Error.propTypes = {
    match: PropTypes.object.isRequired,
}

export default Error