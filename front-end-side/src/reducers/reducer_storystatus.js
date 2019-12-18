import { SET_USER_STORY_ID } from '../actions';

const INITIAL_STATE = {
  userStoryID: null
};

export default (state = INITIAL_STATE, action) => {
  const { payload } = action
  switch (action.type) {
    case SET_USER_STORY_ID: {
      return {...state, userStoryID: payload}
    }
    default:
      return state
  }
}