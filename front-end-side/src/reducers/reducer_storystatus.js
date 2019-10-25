import { AUDIO_PLAY, UPDATE_STATUS_SUBTITLE, RESET_STORY_STATUS, SET_USER_STORY_ID } from '../actions';

const INITIAL_STATE = {
  isAudioPlay: false,
  isAudioPause: true,
  showSubtitle: false
};

export default (state = INITIAL_STATE, action) => {
  const { payload } = action
  switch (action.type) {
    case AUDIO_PLAY: {
      return {...state, isAudioPlay: true }
    }
    case UPDATE_STATUS_SUBTITLE: {
      return {...state, showSubtitle: action.payload}
    }
    // case RESET_STORY_STATUS: {
    //   return {...INITIAL_STATE}
    // }
    case SET_USER_STORY_ID: {
      return {...state, userStoryID: payload}
    }
    default:
      return state
  }
}