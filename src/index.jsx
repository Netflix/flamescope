import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader'
import { Provider } from 'react-redux'
import { createStore } from 'redux'
import { HashRouter } from 'react-router-dom'
import rootReducer from './reducers'
import App from './App'

let store = createStore(rootReducer)

const render = (Component) => {
  ReactDOM.render(
    <Provider store={store}>
      <AppContainer>
        <HashRouter>
          <Component />
        </HashRouter>
      </AppContainer>
    </Provider>,
    document.getElementById('root'),
  )
}

render(App)
if (process.env.NODE_ENV === 'development' && module.hot) {
  module.hot.accept('./App', () => { render(App) })
}