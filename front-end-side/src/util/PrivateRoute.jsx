import React from 'react';
import { connect } from 'react-redux';
import { Redirect, Route } from 'react-router-dom';
import ReactLoading from 'react-loading';

const PrivateRoute = ({ component: Component, authInfo, loading, ...rest }) => {
  
  if (loading.page) {
    return <div className="react-spinner-container "><ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105}  /></div>
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