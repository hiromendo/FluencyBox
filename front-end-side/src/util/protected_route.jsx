import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';

class ProtectedRoute extends React.Component {

  render() {
    const { Component, routeConfig : { path, exact }, authInfo, loading } = this.props;
    if (loading) {
      return (
        <h3>Loading....</h3>
      )
    }
    else if (authInfo.isAuthenticated) {
      return (
        <Route path={path} exact={exact} component ={Component} />
      )
    } else {
      return <Redirect to={{
        pathname: "/",
        from: this.props.location
      }} />
    }
  }
}

const mapStateToProps = ({ authInfo, loading }) => ({
  authInfo,
  loading
})

export default connect(mapStateToProps, null, null, { pure: false })(ProtectedRoute)