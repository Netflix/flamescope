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
                    {this.state.files.sort().map(function(filename) {
                        const path = encodeURIComponent(filename);
                        return (
                            <List.Item style={styles.listItem} as='a' href={`/#/heatmap/${path}`} key={filename}>
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
