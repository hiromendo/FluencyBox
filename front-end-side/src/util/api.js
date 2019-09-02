import base64 from 'base-64';

const BASE_URL = 'http://127.0.0.1:5000';

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