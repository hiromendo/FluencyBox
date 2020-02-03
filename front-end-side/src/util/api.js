import base64 from 'base-64';

//const BASE_URL = 'http://127.0.0.1:5000';//'http://back-end-withreport-dev.us-west-1.elasticbeanstalk.com';//http://back-end-api-dev4.us-west-1.elasticbeanstalk.com;  //'http://127.0.0.1:5000';//
//const BASE_URL = 'https://back-end-withreport-dev.us-west-1.elasticbeanstalk.com'
const BASE_URL = 'http://127.0.0.1:5000'
export const updateUserInfo = (request, uid) => {
  const { userInfo } = request
  try {
    const UPDATE_USER_INFO_ENDPOINT = `${BASE_URL}/users/${uid}`;
    const jwtToken = localStorage.getItem('access_token');

    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'application/json');
    headers.set('Content-Type', 'application/json; charset=UTF-8');
    
    const parameters = {
      method: 'PUT',
      headers,
      body: JSON.stringify(userInfo)
    }

    return fetch(UPDATE_USER_INFO_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        case 404: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json()
      }
      
    })
    .catch(error => {
      throw Error(error)
    })
  } catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const getUserInfoAPI = request => {
  try {
    const { uid } = request;
    const GET_USER_ENDPOINT = `${BASE_URL}/users/${uid}`;
    let headers = new Headers();
    const jwtToken = localStorage.getItem('access_token')
    headers.set('x-access-token', jwtToken);
  
    const parameters = {
      method: 'GET',
      headers
    }
  
    return fetch(GET_USER_ENDPOINT, parameters)
      .then(response => {
        return response.json()
      })
      .catch(error => {
        throw Error(error)
      }) 

  }
  catch (error) {
    console.error(error)
    throw Error (error)
  }
}

export const loginUserAPI = request => {
  const { userInfo } = request;

  const LOGIN_API_ENDPOINT = `${BASE_URL}/login`;
  let headers = new Headers();
  headers.set('Authorization', 'Basic ' + base64.encode(userInfo.userName + ":" + userInfo.password));

  const parameters = {
    method: 'POST',
    headers,
  }

  return fetch(LOGIN_API_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 401: {
          return Promise.reject('Invalid Credentials -- Please Try Again');
        }
        case 500: {
          return Promise.reject('Server is down at the moment -- Please Try Again');
        }
        default:
          return response.json()
      }
      
    })
    .catch(error => {
      throw Error(error)
    })
}

export const registerUserAPI = request => {
  const { userInfo } = request;

  const REGISTER_API_ENDPOINT = `${BASE_URL}/users`;
  const parameters = {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json; charset=UTF-8'
    },
    body: JSON.stringify(userInfo),
  }

  return fetch(REGISTER_API_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(data.message);
          })
        }
        case 500: {
          return Promise.reject('Server is down at the moment -- Please Try Again');
        }
        default: 
          return response.json()
      }
      
    })
    .catch(error => {
      throw Error(error)
    })
}

export const acquireJWTToken = refresh_token  => {
  const REFRESH_TOKEN_ENDPOINT = `${BASE_URL}/access_tokens`;
  let headers = new Headers();
  headers.set('x-refresh-token', refresh_token );
  const parameters = {
    method: 'POST',
    headers
  }

  return fetch(REFRESH_TOKEN_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 401: {
          return response.json().then(data => {
            return Promise.reject(`${data.message} -- Please try logging in again`)
          })
        }
        default:
          return response.json()
      }
    })
    .catch(error => {
      throw Error(error)
    })
}

export const updatePassWordAPI = request => {
  const { uid, currentPassword, password, confirmPassword } = request;
  try {
    const UPDATE_PASSWORD_ENDPOINT = `${BASE_URL}/users/${uid}/password`;
    const jwtToken = localStorage.getItem('access_token');

    const obj = {
      'current_password': currentPassword,
      password,
      'confirm_password': confirmPassword
    }
  
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'application/json');
    headers.set('Content-Type', 'application/json; charset=UTF-8');
  
    const parameters = {
      method: 'PUT',
      headers,
      body: JSON.stringify(obj)
    }

    return fetch(UPDATE_PASSWORD_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        case 500: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json();
      }
    })
  }
  catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const updateProfilePictureAPI = request => {
  const { uid, data } = request;
  try {
    const UPDATE_PROFILE_PIC_ENDPOINT = `${BASE_URL}/users/${uid}/profile_picture`;
    const jwtToken = localStorage.getItem('access_token');

    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'x-www-form-urlencoded');
    /* it seems when uploading a file through fetch, you must omit this part 
    https://stackoverflow.com/questions/36067767/how-do-i-upload-a-file-with-the-js-fetch-api#answer-49510941
    */
    // headers.set('Content-Type', 'x-www-form-urlencoded; charset=UTF-8'); 
    const parameters = {
      method: 'PUT',
      headers,
      body: data
    }

    return fetch(UPDATE_PROFILE_PIC_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json();
      }
    })
  }
  catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const resetPasswordAPI = request => {
  const { email_address } = request;
  try {
    const RESET_PASSWORD_ENDPOINT = `${BASE_URL}/reset_password`;;
    let headers = new Headers();
    headers.set('Accept', 'application/json');
    headers.set('Content-Type', 'application/json; charset=UTF-8');

    const obj = { email_address }

    const parameters = {
      method: 'POST',
      headers,
      body: JSON.stringify(obj)
    }

    return fetch(RESET_PASSWORD_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        case 404: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        case 500: {
          return response.json().then(data => {
            return Promise.reject('Server is down at the moment -- Please Try Again')
          })
        }
        default: 
          return response.json();
      }
    })

  } catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const getAllStoriesAPI = () => {
  const uid = localStorage.getItem('uid');
  try {
    const GET_ALL_STORIES_ENDPOINT = `${BASE_URL}/story?uid=${uid}&page=1&per_page=20`; /* we can custome the query params later... */
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
  
    const parameters = {
      method: 'GET',
      headers
    }

    return fetch(GET_ALL_STORIES_ENDPOINT, parameters)
      .then(response => {
        return response.json()
      })
      .catch(error => {
        throw Error(error)
      })
  }
  catch (error) {
    console.error(error);
    throw Error(error);
  }
}

export const getStoryData = request => {
  const { story_uid, user_uid } = request
  try {
    const GET_STORY_DATA_ENDPOINT = `${BASE_URL}/start_story`;
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Content-Type', 'application/json; charset=UTF-8');
    headers.set('Accept', 'application/json');
    const obj = {
       story_uid,
       user_uid
    }

    const parameters = {
      method: 'POST',
      headers,
      body: JSON.stringify(obj)
    }

    return fetch(GET_STORY_DATA_ENDPOINT, parameters)
      .then(response => {
        return response.json()
      })
      .catch(error => {
        throw Error(error)
      }) 
  } catch (error) {
      console.error(error);
      throw Error(error);
  }
}

export const getStorySceneAPI = request => {
  const { user_story_uid, next_scene_order } = request;
  try {
    const GET_STORY_SCENE_ENDPOINT = `${BASE_URL}/get_story_scene?uid=${user_story_uid}&order=${next_scene_order}`;
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    const parameters = {
      method: 'GET',
      headers
    }

    return fetch(GET_STORY_SCENE_ENDPOINT, parameters)
      .then(response => {
        return response.json();
      })
      .catch(error => {
        throw Error(error)
      }) 
  } catch (error) {
      console.error(error);
      throw Error(error);
  }
}

export const getNextSceneAPI = request => {
  try {
    const USER_RESPONSE_NEXT_SCENE_ENDPOINT = `${BASE_URL}/user_response`;
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'x-www-form-urlencoded');

    const parameters = {
      method: 'POST',
      headers,
      body: request
    }

    return fetch(USER_RESPONSE_NEXT_SCENE_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json();
      }
    })
  } catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const completeStoryAPI = request => {
  try {
    const COMPLETE_STORY_ENDPOINT = `${BASE_URL}/complete_story`;
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'application/json');
    headers.set('Content-Type', 'application/json; charset=UTF-8');

    const parameters = {
      method: 'POST',
      headers,
      body: JSON.stringify(request)
    }

    return fetch(COMPLETE_STORY_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json();
      }
    })
  } catch (error) {
    console.error(error);
    throw Error(error)
  }
}

export const getAllReportsAPI = uid => {
  try {
    const GET_ALL_REPORTS_ENDPOINT = `${BASE_URL}/reports?uid=${uid}&page=1&per_page10`;
    const jwtToken = localStorage.getItem('access_token');
    let headers = new Headers();
    headers.set('x-access-token', jwtToken);

    const parameters = {
      method: 'GET',
      headers
    }

    return fetch(GET_ALL_REPORTS_ENDPOINT, parameters)
    .then(response => {
      switch (response.status) {
        case 400: {
          return response.json().then(data => {
            return Promise.reject(`${data.message}`)
          })
        }
        default: 
          return response.json();
      }
    })
  } catch (error) {
    console.error(error);
    throw Error(error)
  }
}