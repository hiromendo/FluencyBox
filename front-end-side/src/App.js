import React from 'react';
import { connect } from 'react-redux';
import { Switch, Route, withRouter } from 'react-router-dom';
import { CSSTransition, TransitionGroup } from 'react-transition-group'
import ReactLoading from 'react-loading';

import NavBar from './components/navbar/NavBar';

import { HomePage, 
  LoginPage, 
  AppLayOut, 
  UserProfilePage, 
  updateProfileInfoPage, 
  updatePasswordPage, 
  UpdatePicturePage, 
  resetPasswordPage,
  ReportDashBoard
} from './components/pages';

import PrivateRoute from './util/PrivateRoute';
import SingleStoryPage from './components/pages/SingleStoryPage/SingleStoryPage';
import StartStoryPage from './components/pages/StartStoryPage/StartStoryPage';
import ReportCard from './components/reportCard/ReportCard';
import { endLoading, getCurrentUser, getAccessToken, removeCurrentUser, resetAlert, getAllStories, getAllReports } from './actions';

import "./App.scss";

class App extends React.Component {

  constructor(props) {
    super(props);
    this.logOffUser = this.logOffUser.bind(this);
    this.renderAllReportsLinks = this.renderAllReportsLinks.bind(this);
    this.renderAllStoriesLinks = this.renderAllStoriesLinks.bind(this);
    this.renderAllStartStoriesLinks = this.renderAllStartStoriesLinks.bind(this);
    this.renderSpinnerLoading = this.renderSpinnerLoading.bind(this);
  }

  componentDidMount() {
    if (localStorage.access_token && localStorage.uid) {
      const infoObjToken = {};
      infoObjToken.uid = localStorage.uid;
      this.props.getCurrentUser(infoObjToken);
      this.props.getAllStories();
      this.props.getAllReports(infoObjToken.uid)
    } else if (localStorage.refresh_token) {
      this.props.getAccessToken(localStorage.refresh_token);
    } else {
      this.props.endLoading()
    }
  }

  renderAllReportsLinks() {
    const { reports } = this.props.reportsStatus;
    const listReportCardsRoutes = reports.map(info => {
      return (
        <Route
          exact
          path={`/report/${info.uid}`}
          key={info.uid}
          render={(props) => <ReportCard {...info} routeProps={props} />} />
      )
    })

    return listReportCardsRoutes
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
    const listStartRoutes = story.map(info => {
      return (
        <Route 
          exact 
          path={`/story/${info.uid}/start`} 
          key={info.uid} 
          render={(props) => <StartStoryPage {...info} routeProps={props} />} />
      )
    })
    return listStartRoutes
  }

  renderSpinnerLoading() {
    return (
      <div className="react-spinner-container ">
        <ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105}  />
      </div>
    )
  }

  render() {
    const { location, loading } = this.props;
    return (
      <div className="App">
        <header>
          {(location.pathname !== "/login" && location.pathname !=='/resetpassword') ? <NavBar logOffUser={this.logOffUser} /> : null}
        </header>
        {loading.page ? this.renderSpinnerLoading() :
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
                <PrivateRoute path='/reports' component={ReportDashBoard} />
                {this.renderAllStoriesLinks()}
                {this.renderAllStartStoriesLinks()}
                {this.renderAllReportsLinks()}
                <Route path="*" component={() => "404 not found" } />
              </Switch>
            </CSSTransition>
          </TransitionGroup>

        </main>
        }
      </div>
    )
  }
}

const mapStateToProps = ({ storiesInfo, loading, reportsStatus }) => ({
  storiesInfo,
  loading,
  reportsStatus
})

const mapDispatchToProps = {
  endLoading,
  getCurrentUser,
  getAccessToken,
  removeCurrentUser,
  resetAlert,
  getAllStories,
  getAllReports
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(App));