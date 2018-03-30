import { combineReducers } from 'redux'
import navbar from './NavbarReducer'


const rootReducer = combineReducers({
  navbar,
})

export default rootReducer