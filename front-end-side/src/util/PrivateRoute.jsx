import React from 'react';
import { connect } from 'react-redux';
import { Redirect, Route } from 'react-router-dom';

const PrivateRoute = ({ component: Component, authInfo, loading, ...rest }) => {
  
  if (loading) {
    return <h3>Loading....</h3>
  }

  return (
    <Route {...rest} render={(props) => (
      authInfo.isAuthenticated === true
        ? <Component {...props} />
        : <Redirect to={{
            pathname: '/login',
            state: { from: props.location }
          }} />
    )} />
  )
}


const mapStateToProps = ({ authInfo, loading }) => ({
  authInfo,
  loading
})

export default connect(mapStateToProps)(PrivateRoute)