import { SET_REPORT_CONTENTS, REMOVE_REPORT_CONTENTS, REPORT_CONTENT_LOADED, RESET_REPORT_CONTENTS } from '../actions';

const INITIAL_STATE = {
  isReportContentFinishedLoaded: false
};

export default (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case REPORT_CONTENT_LOADED: {
      return {...state, isReportContentFinishedLoaded: true }
    }
    case SET_REPORT_CONTENTS: {
      return {...state, ...action.payload}
    }
    case REMOVE_REPORT_CONTENTS: {
      return INITIAL_STATE
    }
    case RESET_REPORT_CONTENTS: {
      return INITIAL_STATE
    }
    default:
      return state
  }
}