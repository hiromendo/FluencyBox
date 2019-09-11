import React from 'react';
import { connect } from 'react-redux';

class AppLayOut extends React.Component {

  render() {
    const { first_name } = this.props.userInfo
    return (
      <>
        <main>
          <div>Insert stories here...</div>
        </main>
      </>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  userInfo: authInfo.serverResponse.user
})


export default connect(mapStateToProps)(AppLayOut);