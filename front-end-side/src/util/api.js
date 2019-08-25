import base64 from 'base-64';

export const getUserInfoAPI = request => {
  const { uid } = request;
  const GET_USER_ENDPOINT = `http://127.0.0.1:5000/users/${uid}`;
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
}

export const loginUserAPI = request => {
  const { userInfo } = request;

  const LOGIN_API_ENDPOINT = 'http://127.0.0.1:5000/login';
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

  const REGISTER_API_ENDPOINT = 'http://127.0.0.1:5000/users';
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
      return response.json()
    })
}