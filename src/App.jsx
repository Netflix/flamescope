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

import React from 'react'
import { Container } from 'semantic-ui-react'
import { Route, Switch, Redirect } from 'react-router-dom'
import { FileList, Heatmap, FlameGraph, DifferentialFlameGraph, ElidedFlameGraph, Navbar, Error } from './components'

import '../semantic/semantic.less'

const App = () => (
  <div>
    <Navbar />
    <Container>
      <Switch>
        <Route exact path="/" component={FileList}/>
        <Route exact path="/heatmap/:type/:filename" component={Heatmap} />
        <Route exact path="/flamegraph/:type/:filename/:start/:end" component={FlameGraph} />
        <Route exact path="/flamegraph/:type/:filename" component={FlameGraph} />
        <Route exact path="/compare/:compareType/:compareFilename/:compareStart/:compareEnd" component={FileList} />
        <Route exact path="/compare/:compareType/:compareFilename" component={FileList} />
        <Route exact path="/compare/:compareType/:compareFilename/:compareStart/:compareEnd/heatmap/:type/:filename" component={Heatmap} />
        <Route exact path="/compare/:compareType/:compareFilename/heatmap/:type/:filename" component={Heatmap} />
        <Route exact path="/differential/:type/:filename/:start/:end/compare/:compareType/:compareFilename/:compareStart/:compareEnd" component={DifferentialFlameGraph} />
        <Route exact path="/differential/:type/:filename/:start/:end/compare/:compareType/:compareFilename" component={DifferentialFlameGraph} />
        <Route exact path="/differential/:type/:filename/compare/:compareType/:compareFilename/:compareStart/:compareEnd" component={DifferentialFlameGraph} />
        <Route exact path="/differential/:type/:filename/compare/:compareType/:compareFilename" component={DifferentialFlameGraph} />
        <Route exact path="/elided/:type/:filename/:start/:end/compare/:compareType/:compareFilename/:compareStart/:compareEnd" component={ElidedFlameGraph} />
        <Route exact path="/elided/:type/:filename/:start/:end/compare/:compareType/:compareFilename" component={ElidedFlameGraph} />
        <Route exact path="/elided/:type/:filename/compare/:compareType/:compareFilename/:compareStart/:compareEnd" component={ElidedFlameGraph} />
        <Route exact path="/elided/:type/:filename/compare/:compareType/:compareFilename" component={ElidedFlameGraph} />
        <Route exact path="/error/:code" component={Error} />
        <Redirect to="/error/404" />
      </Switch>
    </Container>
  </div>
)

export default App
