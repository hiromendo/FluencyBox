import React from 'react';
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
    return (
      <main>
        <h2>User Profile</h2>
        <div>
          <img id="profile-image" src="http://placekitten.com/300/300" alt="profile"/>
        </div>
        
      </main>

    )
  }
}

export default UserProfilePage;