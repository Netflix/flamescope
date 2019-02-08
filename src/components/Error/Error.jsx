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
import { Header, Segment } from 'semantic-ui-react'
import PropTypes from 'prop-types'
import queryString from 'query-string'

const styles = {
    header: {
        marginTop: '75px',
    }
}

class Error extends Component {
    render() {
        const { code } = this.props.match.params
        const query = queryString.parse(this.props.location.search)
        const message = query['message']
        return (
            <div>
                <Header as='h1' style={styles.header}>Error {code}</Header>
                <Segment>{message}</Segment>
            </div>
        )
    }
}

Error.propTypes = {
    match: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
}

export default Error