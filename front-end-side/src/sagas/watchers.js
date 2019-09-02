import { all, takeLatest } from 'redux-saga/effects'

import { getLoginAsync, sendRegisterAsync, gettingUserInfo, getAccessToken, updateUserInfoAsync, updatePasswordAsync } from './authenticationSaga';
import * as types from './../actions';

function* actionWatcher() {
  yield takeLatest(types.GET_CURRENT_USER, gettingUserInfo);
  yield takeLatest(types.GET_LOGIN, getLoginAsync);
  yield takeLatest(types.SEND_REGISTER, sendRegisterAsync);
  yield takeLatest(types.GET_ACCESS_TOKEN, getAccessToken);
  yield takeLatest(types.UPDATE_USER_INFO, updateUserInfoAsync);
  yield takeLatest(types.UPDATE_PASSWORD, updatePasswordAsync);
}

export default function* rootSaga() {
  yield all([
    actionWatcher(),
  ]);
}