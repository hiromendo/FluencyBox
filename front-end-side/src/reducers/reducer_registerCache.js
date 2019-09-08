
import { REGISTER_CACHE, REGISTER_CLEAR } from '../actions';

let INITIAL_STATE = {
  firstname: '',
  lastname: '',
  userName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
}

export default (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case REGISTER_CACHE: {
      return {...state, ...action.infoObj}
    }
    case REGISTER_CLEAR: {
      return {...state, ...INITIAL_STATE}
    }
    default: 
      return state;
  }
}