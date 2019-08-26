import { put, call } from 'redux-saga/effects';
import { loginUserAPI, getUserInfoAPI, registerUserAPI, acquireJWTToken } from './../util/api'

import {
  START_LOADING,
  END_LOADING,
  SET_CURRENT_USER,
  DISPLAY_ALERT
 } from '../actions'


 export function* gettingUserInfo({ userInfo }) {
   const userInfoResponse = yield call(getUserInfoAPI, userInfo);
   yield settingUserInfo(userInfoResponse);
 }

 export function* settingUserInfo(response, history = null) {
  yield put({ type: SET_CURRENT_USER, payload: { user: response }})
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
    yield put({ type: DISPLAY_ALERT, payload: { errorMessage: error.message, status: 'error' } })
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
    const userInfoResponse = yield call(getUserInfoAPI, registerResponse);
    yield settingUserInfo(userInfoResponse, history);

  } catch(error) {
    console.error(error.message)
    yield put({ type: DISPLAY_ALERT, payload: { errorMessage: error.message, status: 'error' } })
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
    yield put({ type: DISPLAY_ALERT, payload: { errorMessage: error.message, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}