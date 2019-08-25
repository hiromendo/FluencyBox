import React from 'react';
import { connect } from 'react-redux';

import { Switch, Route } from 'react-router-dom';

import { HomePage, LoginPage , AppLayOut, UserProfilePage } from './components/pages';

import PrivateRoute from './util/PrivateRoute';
import { endLoading, getCurrentUser } from './actions';

import "./App.scss";

class App extends React.Component {
  componentDidMount() {
    if (localStorage.access_token && localStorage.uid) {
      const infoObj = {};
      infoObj.uid = localStorage.uid;
      this.props.getCurrentUser(infoObj)
    } else {
      this.props.endLoading()
    }
  }

  render() {
    return (
      <div className="App">
        <h1>Fluency Box</h1>
        <Switch>
          <Route exact path="/" component={HomePage}/>
          <Route exact path="/login" component={LoginPage}/>
          <PrivateRoute path='/app' component={AppLayOut} />
          <PrivateRoute path='/userprofile' component={UserProfilePage} />
          <Route path="*" component={() => "404 not found" } />
        </Switch>
      </div>
    )
  }
}

const mapDispatchToProps = {
  endLoading,
  getCurrentUser
}

export default connect(null, mapDispatchToProps)(App);