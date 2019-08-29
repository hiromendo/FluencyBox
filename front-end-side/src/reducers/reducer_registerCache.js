
import { REGISTER_CACHE } from '../actions';

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
    default: 
      return state;
  }
}