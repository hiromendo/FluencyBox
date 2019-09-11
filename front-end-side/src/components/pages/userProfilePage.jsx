import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './userProfilePage.scss';

class UserProfilePage extends React.Component {
  
  render() {
    const { first_name, last_name, phone_number, user_name, email_address, profile_picture } = this.props.userInfo;
    return (
      <main>
        <div className="profile-container">
          <h2>User Profile</h2>
          <img id="profile-image" src={profile_picture} alt="profile"/>
          <ul id="profile-info">
            <li>First Name: {first_name}</li>
            <li>Last Name: {last_name}</li>
            <li>Phone Number: {phone_number ? phone_number : 'N/A'}</li>
            <li>UserName: {user_name}</li>
            <li>Email: {email_address}</li>
          </ul>
        </div>
        <div>
          <Link to="/updatePassword">Update Password</Link>
          <br/>
          <Link to="/updateprofileinfo">Update Profile Info</Link>
          <br/>
          <Link to="/updatePicture">Update Profile Picture</Link>
        </div>
      </main>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  userInfo: authInfo.serverResponse.user
})



export default connect(mapStateToProps)(UserProfilePage);