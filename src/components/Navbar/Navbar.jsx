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
import { Header, Menu, Breadcrumb, Container } from 'semantic-ui-react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

const styles = {
    header: {
        fontWeight: 300,
        fontSize: '22px',
        textTransform: 'uppercase',
        color: '#9D9D9D',
        letterSpacing: '2px',
    },
    breadcrumb: {
        fontWeight: 300,
    },
    icon: {
        color: '#D9D9D9',
    }
}

class Navbar extends Component {
    render() {
        const { breadcrumbs } = this.props

        return (
            <Menu fixed='top' color='grey' inverted>
                <Container>
                    <Menu.Item>
                        <Header as='h2' style={styles.header} inverted><Link to="/#/">🔥FlameScope</Link></Header>
                    </Menu.Item>
                    <Menu.Item>
                        <Breadcrumb style={ styles.breadcrumb } icon='right angle' size='small' sections={ breadcrumbs } />
                    </Menu.Item>
                </Container>
            </Menu>
        )
    }
}

Navbar.propTypes = {
    breadcrumbs: PropTypes.array.isRequired,
}

const mapStateToProps = state => {
    const { breadcrumbs } = state.navbar
    return {
        breadcrumbs: breadcrumbs
    }
}

export default connect(
    mapStateToProps,
)(Navbar)