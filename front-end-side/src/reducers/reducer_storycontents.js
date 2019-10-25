import { SET_STORY_CONTENTS, REMOVE_STORY_CONTENTS, STORY_CONTENT_LOADED, SET_USER_STORY_ID } from '../actions';

const INITIAL_STATE = {
  isContentFinishedLoaded: false
};

export default (state = INITIAL_STATE, action) => {
  const { payload } = action
  switch (action.type) {
    case STORY_CONTENT_LOADED: {
      return {...state, isContentFinishedLoaded: true }
    }
    case SET_STORY_CONTENTS: {
      return {...state, ...action.payload}
    }
    case REMOVE_STORY_CONTENTS: {
      return INITIAL_STATE
    }
    case SET_USER_STORY_ID: {
      return {...state, userStoryID: payload}
    }
    default:
      return state
  }
}