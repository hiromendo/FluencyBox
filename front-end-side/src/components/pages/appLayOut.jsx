import React from 'react';
import { connect } from 'react-redux';

class AppLayOut extends React.Component {

  render() {
    const { first_name } = this.props.userInfo
    return (
      <>
        <main>
          <h2>Welcome {first_name}!</h2>
        </main>
      </>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  userInfo: authInfo.serverResponse.user
})


export default connect(mapStateToProps)(AppLayOut);