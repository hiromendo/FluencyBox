import { SET_ALL_REPORTS, UPDATE_FETCHING_REPORTS } from '../actions';

const INITIAL_STATE = {
  reports: [],
  isFetchingReports: false,
  pagination: {},
}

export default (state = INITIAL_STATE, action) => {
  const { payload } = action
  switch( action.type) {
    case UPDATE_FETCHING_REPORTS: {
      return { ...state, isFetchingReports: payload }
    }
    case SET_ALL_REPORTS: {
      return { ...state, reports: payload.reports, pagination: payload.pagination}
    }
    default: 
      return state
  }
}
