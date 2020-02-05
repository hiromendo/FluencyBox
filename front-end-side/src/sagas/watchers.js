import { all, takeLatest } from 'redux-saga/effects'

import { getLoginAsync, 
  sendRegisterAsync, 
  gettingUserInfo, 
  getAccessToken, 
  updateUserInfoAsync, 
  updatePasswordAsync,
  updateProfilePictureAsync,
  resetPasswordAsync,
  getAllStoriesAsync,
  removeUserAsync,
  getStoryStartedAsync,
  getStoryContentAsync,
  getNextSceneAsync,
  completeStoryAsync,
  getAllReportsAsync,
  getReportContentsAsync
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
  yield takeLatest(types.GET_ALL_STORIES, getAllStoriesAsync);
  yield takeLatest(types.REMOVE_CURRENT_USER_ASYNC, removeUserAsync);
  yield takeLatest(types.GET_STORY_STARTED, getStoryStartedAsync);
  yield takeLatest(types.GET_STORY_CONTENTS, getStoryContentAsync);
  yield takeLatest(types.GET_NEXT_SCENE_ASYNC, getNextSceneAsync);
  yield takeLatest(types.COMPLETE_STORY, completeStoryAsync);
  // Report Scores
  yield takeLatest(types.GET_ALL_REPORTS, getAllReportsAsync);
  yield takeLatest(types.GET_REPORT_CONTENTS, getReportContentsAsync);
}

export default function* rootSaga() {
  yield all([
    actionWatcher(),
  ]);
}