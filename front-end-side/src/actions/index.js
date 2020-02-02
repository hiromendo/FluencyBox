
export const START_LOADING = 'START_LOADING'; //loading for page
export const END_LOADING = 'END_LOADING';
export const START_LOADING_CONTENT = 'START_LOADING_CONTENT'; //loading for content
export const END_LOADING_CONTENT = 'END_LOADING_CONTENT'; //loading for content

export const GET_LOGIN = 'GET_LOGIN';
export const SEND_REGISTER = 'SEND_REGISTER';
export const UPDATE_USER_INFO = 'UPDATE_USER_INFO';
export const UPDATE_PASSWORD = 'UPDATE_PASSWORD';
export const UPDATE_PROFILE_PICTURE = 'UPDATE_PROFILE_PICTURE';
export const RESET_PASSWORD = 'RESET_PASSWORD';

export const GET_CURRENT_USER = 'GET_CURRENT_USER';
export const SET_CURRENT_USER = 'SET_CURRENT_USER';
export const REMOVE_CURRENT_USER_ASYNC = 'REMOVE_CURRENT_USER_ASYNC';
export const REMOVE_CURRENT_USER = 'REMOVE_CURRENT_USER';

export const GET_ACCESS_TOKEN = 'GET_ACCESS_TOKEN';

export const RESET_ALERT_MESSAGE = 'RESET_ALERT_MESSAGE';
export const DISPLAY_ERROR_LOGIN = 'DISPLAY_ERROR_LOGIN';
export const DISPLAY_ERROR_UPDATE = 'DISPLAY_ERROR_UPDATE';
export const DISPLAY_SUCCESS = 'DISPLAY_SUCCESS';

export const REGISTER_CACHE = 'REGISTER_CACHE';
export const REGISTER_CLEAR = 'REGISTER_CLEAR';

export const GET_ALL_STORIES = 'GET_ALL_STORIES';
export const SET_ALL_STORIES = 'SET_ALL_STORIES';
export const GET_STORY_STARTED = 'GET_STORY_STARTED';
export const GET_STORY_CONTENTS = 'GET_STORY_CONTENTS';
export const SET_STORY_CONTENTS = 'SET_STORY_CONTENTS';
export const REMOVE_STORY_CONTENTS = 'REMOVE_STORY_CONTENTS';
export const STORY_CONTENT_LOADED = 'STORY_CONTENT_LOADED';
export const SET_USER_STORY_ID = 'SET_USER_STORY_ID';

export const RESET_STORY_STATUS = 'RESET_STORY_STATUS';

export const GET_NEXT_SCENE_ASYNC = 'GET_NEXT_SCENE_ASYNC'
export const COMPLETE_STORY = 'COMPLETE_STORY'

//Report Dashboard Actions
export const GET_ALL_REPORTS = 'GET_ALL_REPORTS';
export const UPDATE_FETCHING_REPORTS = 'UPDATE_FETCHING_REPORTS';
export const SET_ALL_REPORTS = 'SET_ALL_REPORTS';

export const startLoading = () => ({
  type: START_LOADING
})

export const endLoading = () => ({
  type: END_LOADING
})

export const startLoadingContent = () => ({
  type: START_LOADING_CONTENT
})

export const getCurrentUser = userInfo => ({
  type: GET_CURRENT_USER,
  userInfo
})

export const getLogin = (userInfo, history) => ({
  type: GET_LOGIN,
  userInfo,
  history
});

export const sendRegister = (userInfo, history) => ({
  type: SEND_REGISTER,
  userInfo,
  history
})

export const updateUserInfo = (userInfo, uid, history) => ({
  type: UPDATE_USER_INFO,
  userInfo,
  uid,
  history
})

export const updatePassword = payload => ({
  type: UPDATE_PASSWORD,
  payload
})

export const resetPassword = payload => ({
  type: RESET_PASSWORD,
  payload
})

export const setCurrentUser = data => ({
  type: SET_CURRENT_USER,
  data
})

export const updateProfilePicture = payload => ({
  type: UPDATE_PROFILE_PICTURE,
  payload
})

export const removeCurrentUser = () => ({
  type: REMOVE_CURRENT_USER_ASYNC
})

export const resetAlert = () => ({
  type: RESET_ALERT_MESSAGE
})

export const displayAlert = (status, errorMessage) => ({
  type: DISPLAY_ERROR_LOGIN,
  payload: {
    status,
    errorMessage
  }
})

export const displayErrorUpdate = payload => ({
  type: DISPLAY_ERROR_UPDATE,
  payload
})

export const displaySuccess = (status, sucessMessage) => ({
  type: DISPLAY_SUCCESS,
  payload: {
    status,
    sucessMessage
  }
})

export const getAccessToken = refresh_token => ({
  type: GET_ACCESS_TOKEN,
  refresh_token
})

export const cacheRegisterInfo = infoObj => ({
  type: REGISTER_CACHE,
  infoObj
})

export const getAllStories = () => ({
  type: GET_ALL_STORIES
})

export const setAllStories = payload => ({
  type: SET_ALL_STORIES,
  payload
})

export const getStoryStarted = payload => ({
  type: GET_STORY_STARTED,
  payload
})

export const getStoryContents = payload => ({
  type: GET_STORY_CONTENTS,
  payload
})

export const removeStoryContents = () => ({
  type: REMOVE_STORY_CONTENTS
})
export const resetStoryStatus = () => ({
  type: RESET_STORY_STATUS
})
///////////////////////////////////
export const getAsyncNextScene = payload => ({
  type: GET_NEXT_SCENE_ASYNC,
  payload
})

export const completeStory = payload => ({
  type: COMPLETE_STORY,
  payload
})

/* Report Dashboard */
export const getAllReports = payload => ({
  type: GET_ALL_REPORTS,
  payload
})