import { combineReducers } from 'redux';
import loadingReducer from './reducer_loading';
import authReducer from './reducer_auth';
import registerCacheReducer from './reducer_registerCache';
const rootReducer = combineReducers({
  loading: loadingReducer,
  authInfo: authReducer,
  registerCache: registerCacheReducer
})

export default rootReducer;