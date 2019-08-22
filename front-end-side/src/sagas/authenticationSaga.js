import { put, call } from 'redux-saga/effects';
import jwt from "jwt-decode";
import { loginUserAPI, getUserInfoAPI, registerUserAPI } from './../util/api'

import {
  START_LOADING,
  END_LOADING,
  SET_CURRENT_USER
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
    console.log(error)
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
    }
    const userInfoResponse = yield call(getUserInfoAPI, registerResponse);
    yield settingUserInfo(userInfoResponse, history);

  } catch(error) {
    console.log(error)
    yield put({ type: END_LOADING });
  }
}
