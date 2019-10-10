import { AUDIO_PLAY, UPDATE_STATUS_SUBTITLE } from '../actions';

const INITIAL_STATE = {
  isAudioPlay: false,
  isAudioPause: false,
  showSubtitle: false
};

export default (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case AUDIO_PLAY: {
      return {...state, isAudioPlay: true }
    }
    case UPDATE_STATUS_SUBTITLE : {
      return {...state, showSubtitle: action.payload}
    }
    default:
      return state
  }
}