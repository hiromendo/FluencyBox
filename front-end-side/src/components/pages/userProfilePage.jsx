import React from 'react';
import { connect } from 'react-redux';
import './userProfilePage.scss';

class UserProfilePage extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isProfileFormEditable : false,
      isPassWordFormEditable: false
    }
  }
  render() {
    const { first_name, last_name, phone_number, user_name, email_address } = this.props.userInfo;
    return (
      <main>
        <div className="profile-container">
          <h2>User Profile</h2>
          <img id="profile-image" src="http://placekitten.com/300/300" alt="profile"/>
          <ul id="profile-info">
            <li>First Name: {first_name}</li>
            <li>Last Name: {last_name}</li>
            <li>Phone Number: {phone_number ? phone_number : 'N/A'}</li>
            <li>UserName: {user_name}</li>
            <li>Email: {email_address}</li>
          </ul>
        </div>
        <div className="update-container">
          <div className="btn">Update Profile Picture</div>
          <div className="btn">Update Info</div>
        </div>
        <div className="update-container">
          <div className="btn">Update Password</div>
        </div>
      </main>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  userInfo: authInfo.serverResponse.user
})



export default connect(mapStateToProps)(UserProfilePage);