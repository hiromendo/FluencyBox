import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './userProfilePage.scss';

class UserProfilePage extends React.Component {
  
  render() {
    const { user_name, email_address, profile_picture } = this.props.userInfo;
    return (
      <main className="page">
        <div className="profile-container">
          <h2>Profile</h2>
          <img id="profile-image" src={profile_picture} alt="profile"/>
          <ul id="profile-info">
            <li>UserName: <span>{user_name}</span></li>
            <li>Email: <span>{email_address}</span></li>
          </ul>
          <div className="update-links-container">
            <div className="btn btn-white">
              <Link to="/updatePassword">Update Password</Link>
            </div>
            <div className="btn btn-white">
              <Link to="/updateprofileinfo">Update Profile Info</Link>
            </div>
            <div className="btn btn-white">
              <Link to="/updatePicture">Update Profile Picture</Link>
            </div>
          </div>
        </div>
      </main>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  userInfo: authInfo.serverResponse.user
})



export default connect(mapStateToProps)(UserProfilePage);