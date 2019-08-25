
import { SET_CURRENT_USER, REMOVE_CURRENT_USER, DISPLAY_ALERT } from '../actions'

const INITIAL_STATE = {
  isAuthenticated: false,
  serverResponse: {}
}

export default ( state = INITIAL_STATE, action = {} ) => {
  const { payload } = action
  switch (action.type) {
    case SET_CURRENT_USER:
      return { ...state, isAuthenticated: true, serverResponse: payload.user}
    case REMOVE_CURRENT_USER :
      return { ...state, isAuthenticated: false, serverResponse: {} }
    case DISPLAY_ALERT :
      return { ...state, isAuthenticated: false, serverResponse: { status: payload.status, errorMessage: payload.errorMessage }}
    default:
      return state
  }
}