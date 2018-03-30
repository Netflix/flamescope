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