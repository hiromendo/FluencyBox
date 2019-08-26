import jwtDecode from 'jwt-decode';

export const checkIfAccessTokenExpired = () => {
  if (localStorage.getItem('access_token')) {
    const jwtToken = localStorage.getItem('access_token');
    const expiredSeconds = jwtDecode(jwtToken).exp;
    const now = new Date();
    const expiredDate = new Date(expiredSeconds * 1000);
    return now > expiredDate
  } 
}

export const removeExpiredJWTAccessToken = () => {
  if (localStorage.getItem('access_token')) { 
    const isAccessTokenExpired = checkIfAccessTokenExpired();
    if (isAccessTokenExpired) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('uid');
    }
  }
}