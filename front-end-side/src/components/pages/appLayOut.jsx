import React from 'react';
import { connect } from 'react-redux';

class AppLayOut extends React.Component {

  render() {
    return (
      <div>
        <main>
          <h2>App Dashboard</h2>
        </main>
      </div>
    )
  }
}

const mapStateToProps = ({authInfo}) => ({
  userInfo: authInfo.serverResponse.user
})


export default connect(mapStateToProps)(AppLayOut);