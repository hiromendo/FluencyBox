import React from 'react';
import { connect } from 'react-redux';
import { Redirect, Route } from 'react-router-dom';

const PrivateRoute = ({ component: Component, authInfo, ...rest }) => (
  <Route {...rest} render={(props) => (
    authInfo.isAuthenticated === true
      ? <Component {...props} />
      : <Redirect to={{
          pathname: '/login',
          state: { from: props.location }
        }} />
  )} />
)


const mapStateToProps = ({ authInfo }) => ({
  authInfo
})

export default connect(mapStateToProps)(PrivateRoute)