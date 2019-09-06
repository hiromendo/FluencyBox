import { all, takeLatest } from 'redux-saga/effects'

import { getLoginAsync, 
  sendRegisterAsync, 
  gettingUserInfo, 
  getAccessToken, 
  updateUserInfoAsync, 
  updatePasswordAsync,
  updateProfilePictureAsync,
  resetPasswordAsync
} from './authenticationSaga';
import * as types from './../actions';

function* actionWatcher() {
  yield takeLatest(types.GET_CURRENT_USER, gettingUserInfo);
  yield takeLatest(types.GET_LOGIN, getLoginAsync);
  yield takeLatest(types.SEND_REGISTER, sendRegisterAsync);
  yield takeLatest(types.GET_ACCESS_TOKEN, getAccessToken);
  yield takeLatest(types.UPDATE_USER_INFO, updateUserInfoAsync);
  yield takeLatest(types.UPDATE_PASSWORD, updatePasswordAsync);
  yield takeLatest(types.UPDATE_PROFILE_PICTURE, updateProfilePictureAsync);
  yield takeLatest(types.RESET_PASSWORD, resetPasswordAsync);
}

export default function* rootSaga() {
  yield all([
    actionWatcher(),
  ]);
}