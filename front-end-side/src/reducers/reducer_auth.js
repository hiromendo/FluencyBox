
import { SET_CURRENT_USER, REMOVE_CURRENT_USER } from '../actions'

const INITIAL_STATE = {
  isAuthenticated: false,
  user: {}
}

export default ( state = INITIAL_STATE, action = {} ) => {
  const { payload } = action
  switch (action.type) {
    case SET_CURRENT_USER:
      return { ...state, isAuthenticated: true, user: payload.user}
    case REMOVE_CURRENT_USER :
      return { ...state, isAuthenticated: false, user: {} }
    default:
      return state
  }
}