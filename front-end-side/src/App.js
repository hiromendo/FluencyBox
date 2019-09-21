import React from 'react';
import { connect } from 'react-redux';
import { Switch, Route, withRouter } from 'react-router-dom';
import { CSSTransition, TransitionGroup } from 'react-transition-group'

import NavBar from './components/navbar/NavBar';

import { HomePage, 
  LoginPage, 
  AppLayOut, 
  UserProfilePage, 
  updateProfileInfoPage, 
  updatePasswordPage, 
  UpdatePicturePage, 
  resetPasswordPage 
} from './components/pages';

import PrivateRoute from './util/PrivateRoute';
import SingleStoryPage from './components/pages/SingleStoryPage/SingleStoryPage';
import StartStoryPage from './components/pages/StartStoryPage/StartStoryPage';
import { endLoading, getCurrentUser, getAccessToken, removeCurrentUser, resetAlert, getAllStories } from './actions';

import "./App.scss";


class App extends React.Component {

  constructor(props) {
    super(props);
    this.logOffUser = this.logOffUser.bind(this);
    this.renderAllStoriesLinks = this.renderAllStoriesLinks.bind(this);
    this.renderAllStartStoriesLinks = this.renderAllStartStoriesLinks.bind(this);
  }

  componentDidMount() {
    if (localStorage.access_token && localStorage.uid) {
      const infoObj = {};
      infoObj.uid = localStorage.uid;
      this.props.getCurrentUser(infoObj);
      this.props.getAllStories();
    } else if (localStorage.refresh_token) {
      this.props.getAccessToken(localStorage.refresh_token);
    } else {
      this.props.endLoading()
    }
  }

  logOffUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('uid');
    this.props.removeCurrentUser();
  }

  renderAllStoriesLinks() {
    const { storiesInfo: { story } }  = this.props;
    const listStoryRoutes = story.map(info => {
      return (
        <Route 
          exact 
          path={`/story/${info.uid}`} 
          key={info.uid} 
          render={(props) => <SingleStoryPage {...info} routeProps={props} />} />
      )
    })
    return listStoryRoutes
  }

  renderAllStartStoriesLinks() {
    const { storiesInfo: { story } }  = this.props;
    const listStoryRoutes = story.map(info => {
      return (
        <Route 
          exact 
          path={`/story/${info.uid}/start`} 
          key={info.uid} 
          render={(props) => <StartStoryPage {...info} routeProps={props} />} />
      )
    })
    return listStoryRoutes
  }

  render() {
    const { location} = this.props;
    return (
      <div className="App">
        <header>
          {location.pathname !== "/login" ? <NavBar logOffUser={this.logOffUser} /> : null}
        </header>
        <main>
          <TransitionGroup>
            <CSSTransition
              key={location.key}
              timeout={450}
              classNames="fade"
            >
              <Switch location={location}>
                <Route exact path="/" component={HomePage}/>
                <Route exact path="/login" component={LoginPage}/>
                <Route exact path="/resetpassword" component={resetPasswordPage}/>
                <PrivateRoute path='/app' component={AppLayOut} />
                <PrivateRoute path='/userprofile' component={UserProfilePage} />
                <PrivateRoute path='/updateprofileinfo' component={updateProfileInfoPage} />
                <PrivateRoute path='/updatePassword' component={updatePasswordPage} />
                <PrivateRoute path='/updatePicture' component={UpdatePicturePage} />
                {this.renderAllStoriesLinks()}
                {this.renderAllStartStoriesLinks()}
                <Route path="*" component={() => "404 not found" } />
              </Switch>
            </CSSTransition>
          </TransitionGroup>

        </main>
      </div>
    )
  }
}

const mapStateToProps = ({ storiesInfo }) => ({
  storiesInfo
})

const mapDispatchToProps = {
  endLoading,
  getCurrentUser,
  getAccessToken,
  removeCurrentUser,
  resetAlert,
  getAllStories
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(App));