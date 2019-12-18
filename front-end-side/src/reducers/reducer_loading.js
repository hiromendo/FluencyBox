import { START_LOADING, END_LOADING, START_LOADING_CONTENT, END_LOADING_CONTENT } from '../actions'

// let INITIAL_STATE = true
let INITIAL_STATE = {
  page: true,
  content: true
}

export default (state = INITIAL_STATE, { type }) => {
  switch(type) {
    case START_LOADING:
      return {...state, page: true }
    case START_LOADING_CONTENT:
      return {...state, content: true}
    case END_LOADING:
      return {...state, page: false }
    case END_LOADING_CONTENT:
      return {...state, content: false}
    default:
      return state
  }
}