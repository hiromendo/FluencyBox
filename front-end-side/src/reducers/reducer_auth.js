
import { SET_CURRENT_USER, 
  REMOVE_CURRENT_USER, 
  DISPLAY_ERROR_LOGIN, 
  DISPLAY_SUCCESS, 
  RESET_ALERT_MESSAGE,
  DISPLAY_ERROR_UPDATE
} from '../actions'

const INITIAL_STATE = {
  isAuthenticated: false,
  serverResponse: {}
}

export default ( state = INITIAL_STATE, action = {} ) => {
  const { payload } = action
  switch (action.type) {
    case SET_CURRENT_USER:
      return { ...state,
        isAuthenticated: true,
        serverResponse: {
          ...state.serverResponse,
            status: null,
            user: payload.user
        }
      }
    case REMOVE_CURRENT_USER :
      return { ...state, isAuthenticated: false, serverResponse: {} }
    case RESET_ALERT_MESSAGE : 
      return { ...state, 
        serverResponse: {
          ...state.serverResponse,
          status: null
        }
      }
    case DISPLAY_ERROR_LOGIN :
      return { ...state, serverResponse: { status: payload.status, errorMessage: payload.errorMessage }}
    case DISPLAY_SUCCESS:
      return { ...state, 
        serverResponse: {
          ...state.serverResponse,
          status: payload.status,
          successMessage: payload.successMessage
        }
      }
    case DISPLAY_ERROR_UPDATE: 
      return { ...state,
        serverResponse: {
          ...state.serverResponse,
          status: payload.status,
          errorMessage: payload.errorMessage
        }
      }
    default:
      return state
  }
}