import { put, call, delay } from 'redux-saga/effects';
import { loginUserAPI, 
  getUserInfoAPI, 
  registerUserAPI, 
  acquireJWTToken, 
  updateUserInfo, 
  updatePassWordAPI, 
  updateProfilePictureAPI, 
  resetPasswordAPI,
  getAllStoriesAPI,
  getStoryData,
  getStorySceneAPI,
  getNextSceneAPI,
  completeStoryAPI
} from './../util/api'

import {
  START_LOADING,
  END_LOADING,
  START_LOADING_CONTENT,
  END_LOADING_CONTENT,
  SET_CURRENT_USER,
  REGISTER_CLEAR,
  DISPLAY_ERROR_LOGIN,
  DISPLAY_SUCCESS,
  DISPLAY_ERROR_UPDATE,
  SET_ALL_STORIES,
  REMOVE_CURRENT_USER,
  STORY_CONTENT_LOADED,
  SET_STORY_CONTENTS,
  SET_USER_STORY_ID
 } from '../actions'

export function* getAllStoriesAsync() {
  const serverResponseAllStories = yield call(getAllStoriesAPI);
  yield put( {type: SET_ALL_STORIES, payload: serverResponseAllStories })
}

 export function* gettingUserInfo({ userInfo }) {
   const userInfoResponse = yield call(getUserInfoAPI, userInfo);
   yield settingUserInfo(userInfoResponse);
 }

 export function* settingUserInfo(response, history = null) {
  yield put({ type: SET_CURRENT_USER, payload: { user: response.user }})
  if (history) { yield history.push('/app') }
  yield delay(450);
  yield put({ type: END_LOADING });
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
    yield getAllStoriesAsync(getAllStoriesAPI);
    yield settingUserInfo(userInfoResponse, history);
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
    yield getAllStoriesAsync(getAllStoriesAPI);
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

export function* removeUserAsync() {
  yield delay(50);
  yield put({ type: REMOVE_CURRENT_USER })
}

export function* getStoryStartedAsync({ payload }) {
  //TODO: you must handle on scenario where story is started first time...
  yield put({ type: START_LOADING_CONTENT });
  // debugger
  const isFromStartPage = payload.history.location.pathname.includes('/start');
  if (payload.history.action === 'PUSH' && !isFromStartPage && payload.history) { yield payload.history.push(`/story/${payload.story_uid}/start`) }
  try {
    const serverResponse = yield call(getStoryData, payload);
    if (serverResponse.pending_story) {
      const { user_story_uid, next_scene_order } = serverResponse;
      yield put({ type: SET_USER_STORY_ID, payload: user_story_uid})
      const { history, story_uid } = payload
      const objPayloadScene = {
        payload: {
          user_story_uid,
          next_scene_order,
          story_uid,
          history
        }
      }
      yield getStoryContentAsync(objPayloadScene)
    } else {
      //TODO: handle situation here
      const { user_story_uid } = serverResponse;
      yield put({ type: SET_USER_STORY_ID, payload: user_story_uid})
      yield payload.history.push(`/story/${payload.story_uid}/start`);

      yield put({ type: END_LOADING_CONTENT });
    }
  } catch (error) {
    console.error(error);
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING_CONTENT });
  }
}

export function* getStoryContentAsync({ payload }) {
  yield put({ type: START_LOADING_CONTENT });
  try {
    const serverResponse = yield call(getStorySceneAPI, payload);
    yield put(({ type: STORY_CONTENT_LOADED }))
    yield put({ type: SET_STORY_CONTENTS, payload: serverResponse })
    yield put({ type: END_LOADING_CONTENT });
  } catch (error) {
    console.error(error);
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING_CONTENT });
  }
}

export function* getNextSceneAsync({ payload }) {
  yield put({ type: START_LOADING_CONTENT });
  try {
    const serverResponse = yield call(getNextSceneAPI, payload);
    yield put(({ type: STORY_CONTENT_LOADED }))
    yield put({ type: SET_STORY_CONTENTS, payload: serverResponse })
    yield put({ type: END_LOADING_CONTENT });
  } catch (error) {
    console.error(error);
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING_CONTENT });
  }
}

export function* completeStoryAsync( { payload }) {
  yield put({ type: START_LOADING });
  try {
    const serverResponse = yield call(completeStoryAPI, payload);
    console.log(serverResponse, 'this is server response');
    yield payload.history.push(`/app`);
    yield delay(450);
    yield put({ type: END_LOADING });
  } catch (error) {
    console.error(error);
    yield put({ type: DISPLAY_ERROR_UPDATE, payload: { errorMessage: error, status: 'error' } })
    yield put({ type: END_LOADING });
  }
}