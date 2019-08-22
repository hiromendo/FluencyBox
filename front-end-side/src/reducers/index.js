import { combineReducers } from 'redux';
import loadingReducer from './reducer_loading';
import authReducer from './reducer_auth';
const rootReducer = combineReducers({
  loading: loadingReducer,
  authInfo: authReducer
})

export default rootReducer;