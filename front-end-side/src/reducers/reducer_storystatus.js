import { AUDIO_PLAY, UPDATE_STATUS_SUBTITLE, RESET_STORY_STATUS } from '../actions';

const INITIAL_STATE = {
  isAudioPlay: false,
  isAudioPause: true,
  showSubtitle: false
};

export default (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case AUDIO_PLAY: {
      return {...state, isAudioPlay: true }
    }
    case UPDATE_STATUS_SUBTITLE: {
      return {...state, showSubtitle: action.payload}
    }
    case RESET_STORY_STATUS: {
      return {...INITIAL_STATE}
    }
    default:
      return state
  }
}