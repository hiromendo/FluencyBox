
export const START_LOADING = 'START_LOADING';
export const END_LOADING = 'END_LOADING';

export const GET_LOGIN = 'GET_LOGIN';
export const SEND_REGISTER = 'SEND_REGISTER';

export const GET_CURRENT_USER = 'GET_CURRENT_USER';
export const SET_CURRENT_USER = 'SET_CURRENT_USER';
export const REMOVE_CURRENT_USER = 'REMOVE_CURRENT_USER';

export const GET_ACCESS_TOKEN = 'GET_ACCESS_TOKEN';

export const DISPLAY_ALERT = 'DISPLAY_ALERT';

export const REGISTER_CACHE = 'REGISTER_CACHE';

export const startLoading = () => ({
  type: START_LOADING
})

export const endLoading = () => ({
  type: END_LOADING
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

export const setCurrentUser = data => ({
  type: SET_CURRENT_USER,
  data
})

export const removeCurrentUser = () => ({
  type: REMOVE_CURRENT_USER
})

export const displayAlert = (status, errorMessage) => ({
  type: DISPLAY_ALERT,
  payload: {
    status,
    errorMessage
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