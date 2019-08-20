import { START_LOADING, END_LOADING } from '../actions'

let INITIAL_STATE = true

export default (state = INITIAL_STATE, { type }) => {
  switch(type) {
    case START_LOADING:
      return true
    case END_LOADING:
      return false
    default:
      return state
  }
}