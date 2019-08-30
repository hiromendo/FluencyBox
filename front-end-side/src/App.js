import React from 'react';
import { connect } from 'react-redux';
import { Switch, Route, Link, withRouter } from 'react-router-dom';

import { HomePage, LoginPage , AppLayOut, UserProfilePage } from './components/pages';
import PrivateRoute from './util/PrivateRoute';
import { endLoading, getCurrentUser, getAccessToken, removeCurrentUser } from './actions';

import "./App.scss";

class App extends React.Component {

  constructor(props) {
    super(props);
    this.logOffUser = this.logOffUser.bind(this);
    this.renderNavBar = this.renderNavBar.bind(this);
  }

  componentDidMount() {
    if (localStorage.access_token && localStorage.uid) {
      const infoObj = {};
      infoObj.uid = localStorage.uid;
      this.props.getCurrentUser(infoObj)
    } else if (localStorage.refresh_token) {
      this.props.getAccessToken(localStorage.refresh_token)
    } else {
      this.props.endLoading()
    }
  }

  logOffUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.props.removeCurrentUser();
  }

  renderNavBar() {
    return (
    <nav id="top-nav">
      <ul>
        <li><Link to="/app">Dashboard</Link></li>
        <li><Link to="/userprofile">UserProfile</Link></li>
        <li><Link to="/aboutus">About Us</Link></li>
        <li><a href="#" onClick={this.logOffUser}>Logout</a></li>
      </ul>
    </nav>
    )
  }

  render() {
    const { location } = this.props;
    return (
      <div className="App">
      <header>
        <h1>Fluency Box</h1>
        {location.pathname !== "/login" ? this.renderNavBar() : null}
      </header>
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
  getCurrentUser,
  getAccessToken,
  removeCurrentUser
}

export default withRouter(connect(null, mapDispatchToProps)(App));