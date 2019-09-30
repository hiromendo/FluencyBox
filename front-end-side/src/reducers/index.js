import { combineReducers } from 'redux';
import loadingReducer from './reducer_loading';
import authReducer from './reducer_auth';
import registerCacheReducer from './reducer_registerCache';
import storiesReducer from './reducer_stories';
import storyContentsReducer from './reducer_storycontents';
const rootReducer = combineReducers({
  loading: loadingReducer,
  authInfo: authReducer,
  registerCache: registerCacheReducer,
  storiesInfo: storiesReducer,
  storyContent: storyContentsReducer
})

export default rootReducer;