import React, { Component } from 'react'
import { Segment, Dimmer, Loader, List } from 'semantic-ui-react'

const styles = {
    container: {
        top: '75px',
    },
    listItem: {
        fontWeight: 400,
        color: '#000',
    }
}

export default class FileList extends Component {
    constructor(props) {
        super(props);
    
        this.state = {
          files: [],
          loading: false,
        };
    }

    componentDidMount() {
        this.setState({loading: true})
        fetch('/stack/list')
            .then(res => {
                return res.json()
            })
            .then(data => {
                this.setState({files: data, loading: false})
            })
    }

    render() {
        return (
            <Segment style={styles.container}>
                <Dimmer page inverted active={this.state.loading}>
                    <Loader size='massive' inverted>Loading</Loader>
                </Dimmer>    
                <List>
                    {this.state.files.map(function(filename) {
                        return (
                            <List.Item style={styles.listItem} as='a' href={`/#/heatmap/${filename}`} key={filename}>
                                <List.Icon name='file' />
                                <List.Content>{filename}</List.Content>
                            </List.Item>
                        )
                    })}
                </List>
            </Segment>
        )
    }
}