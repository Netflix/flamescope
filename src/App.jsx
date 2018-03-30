import React from 'react'
import { Container } from 'semantic-ui-react'
import { Route, Switch, Redirect } from 'react-router-dom'
import { FileList, Heatmap, FlameGraph, Navbar, Error } from './components'

import '../semantic/semantic.less'

const App = () => (
  <div>
    <Navbar />    
    <Container>
      <Switch>
        <Route exact path="/" component={FileList}/>
        <Route exact path="/heatmap/:filename" component={Heatmap} />
        <Route exact path="/heatmap/:filename/flamegraph/:start/:end" component={FlameGraph} />
        <Route exact path="/error/:code" component={Error} />
        <Redirect to="/error/404" />
      </Switch>
    </Container>
  </div>
)

export default App