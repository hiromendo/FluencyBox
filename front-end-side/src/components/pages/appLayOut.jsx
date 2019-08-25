import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { removeCurrentUser } from '../../actions';


class AppLayOut extends React.Component {

  logOffUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.props.removeCurrentUser();
  }

  render() {
    return (
      <div>
        <h2>App Layout</h2>
        <Link to="/userprofile">Click here to update your profile</Link>
        <div onClick={this.logOffUser.bind(this)}>
          <a href="#">Click here to log off</a>
        </div>
      </div>
    )
  }
}

const mapDispatchToProps = {
  removeCurrentUser
}

export default connect(null, mapDispatchToProps)(AppLayOut);