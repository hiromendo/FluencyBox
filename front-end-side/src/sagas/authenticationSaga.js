import { put, call } from 'redux-saga/effects';
import { loginUserAPI, 
  getUserInfoAPI, 
  registerUserAPI, 
  acquireJWTToken, 
  updateUserInfo, 
  updatePassWordAPI, 
  updateProfilePictureAPI, 
  resetPasswordAPI
} from './../util/api'

import {
  START_LOADING,
  END_LOADING,
  SET_CURRENT_USER,
  REGISTER_CLEAR,
  DISPLAY_ERROR_LOGIN,
  DISPLAY_SUCCESS,
  DISPLAY_ERROR_UPDATE
 } from '../actions'


 export function* gettingUserInfo({ userInfo }) {
   const userInfoResponse = yield call(getUserInfoAPI, userInfo);
   yield settingUserInfo(userInfoResponse);
 }

 export function* settingUserInfo(response, history = null) {
  yield put({ type: SET_CURRENT_USER, payload: { user: response.user }})
  yield put({ type: END_LOADING });
  if (history) { yield history.push('/app') }
}

export function* getLoginAsync (payload) {
  yield put({ type: START_LOADING });
  const { history } = payload;
  try {
    const loginResponse = yield call(loginUserAPI, payload);
    if (loginResponse.access_token && loginResponse.refresh_token) {
      localStorage.setItem('access_token', loginResponse.access_token);
      localStorage.setItem('refresh_token', loginResponse.refresh_token);
      localStorage.setItem('uid', loginResponse.uid);
    }
    const userInfoResponse = yield call(getUserInfoAPI, loginResponse);
    yield settingUserInfo(userInfoResponse, history)
  } catch(error) {
    console.error(error)
    yield put({ type: DISPLAY_ERROR_LOGIN, payload: { errorMessage: error.message, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* sendRegisterAsync (payload) {
  yield put({ type: START_LOADING });
  const { history } = payload;
  try {
    const registerResponse = yield call(registerUserAPI, payload);
    if (registerResponse.access_token && registerResponse.refresh_token) {
      localStorage.setItem('access_token', registerResponse.access_token);
      localStorage.setItem('refresh_token', registerResponse.refresh_token);
      localStorage.setItem('uid', registerResponse.uid);
    }
    yield put({ type: REGISTER_CLEAR })
    const userInfoResponse = yield call(getUserInfoAPI, registerResponse);
    yield settingUserInfo(userInfoResponse, history);

  } catch(error) {
    console.error(error.message)
    yield put({ type: DISPLAY_ERROR_LOGIN, payload: { errorMessage: error.message, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* updateUserInfoAsync (payload) {
  yield put({ type: START_LOADING });
  try {
    yield call(updateUserInfo, payload, payload.uid);
    const obj = { userInfo: { uid: payload.uid } }
    yield gettingUserInfo(obj)
    yield put({ type: DISPLAY_SUCCESS, payload: { successMessage: 'Profile Updated!', status: 'success'} });
    yield put({ type: END_LOADING });
  } catch(error) {
    console.error(error.message)
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error.message, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* getAccessToken (request) {
  const { refresh_token } = request
  try {
    const refreshTokenResponse = yield call(acquireJWTToken, refresh_token);
    if (refreshTokenResponse.access_token && refreshTokenResponse.refresh_token) {
      localStorage.setItem('access_token', refreshTokenResponse.access_token);
      localStorage.setItem('refresh_token', refreshTokenResponse.refresh_token);
      localStorage.setItem('uid', refreshTokenResponse.uid);
    }

    const userInfoResponse = yield call(getUserInfoAPI, refreshTokenResponse);
    yield settingUserInfo(userInfoResponse)
  }
  catch (error) {
    console.error(error.message)
    yield put({ type: DISPLAY_ERROR_LOGIN, payload: { errorMessage: error.message, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* updatePasswordAsync (request) {
  const { payload } = request
  yield put({ type: START_LOADING });
  try {
    const serverResponse = yield call(updatePassWordAPI, payload);
    const { message } = serverResponse;
    yield put({ type: DISPLAY_SUCCESS, payload: { successMessage: message, status: 'success'} });
    yield put({ type: END_LOADING });
  }
  catch (error) {
    console.error(error)
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* updateProfilePictureAsync(request) {
  const { payload } = request;
  yield put({ type: START_LOADING });
  try {
    const serverResponse = yield call(updateProfilePictureAPI, request.payload);
    const { message } = serverResponse
    const obj = { userInfo: { uid: payload.uid } }
    yield gettingUserInfo(obj)
    yield put({ type: DISPLAY_SUCCESS, payload: { successMessage: message, status: 'success'} });
    yield put({ type: END_LOADING });

  } catch (error) {
    console.error(error)
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}

export function* resetPasswordAsync (request) {
  const { payload } = request;
  yield put({ type: START_LOADING });
  try {
    const serverResponse = yield call(resetPasswordAPI, payload);
    const { message } = serverResponse;
    yield payload.history.push('/login');
    yield put({ type: DISPLAY_SUCCESS, payload: { successMessage: message, status: 'success'} });
    yield put({ type: END_LOADING });

  } catch (error) {
    console.error(error)
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}