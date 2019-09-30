import { SET_STORY_CONTENTS, REMOVE_STORY_CONTENTS, STORY_CONTENT_LOADED } from '../actions';

const INITIAL_STATE = {
  isContentFinishedLoaded: false
};

export default (state = INITIAL_STATE, action) => {
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
    default:
      return state
  }
}