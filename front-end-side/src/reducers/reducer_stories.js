
import { SET_ALL_STORIES
} from '../actions'

const INITIAL_STATE = {
  pagination: null,
  status: null,
  story: []
}

export default ( state = INITIAL_STATE, action = {}) => {
  const { payload } = action
  switch(action.type) {
    case SET_ALL_STORIES: 
      return {...state, ...payload }
    default:
      return state 
  }
}