import React from 'react';
import { connect } from 'react-redux';

import Login from '../login/login';
import Register from '../login/register';

import { AlertMessage } from '../alertMessage/alertMessage';

class LoginPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLogginActive: true
    }
  }

  changeState() {
    this.setState(prevState => ({ isLogginActive: !prevState.isLogginActive }))
  }

  renderAlertMessage() {
    const { serverResponse } = this.props.authInfo;
    return serverResponse.status === 'error' ? <AlertMessage typeAlert={serverResponse.status} message={serverResponse.errorMessage} /> : null;
  }

  render() {
    const { isLogginActive } = this.state;
    const current = isLogginActive ? "Register" : "Login";
    return (
      <div>
        {this.props.loading ? (
          <h2>Loading....</h2>
        ) : (
          <div className="login">
            <div className="container">
              {this.renderAlertMessage()}
              {isLogginActive && <Login containerRef={ (ref) => this.current = ref}/>}
              {!isLogginActive && <Register containerRef={ (ref) => this.current = ref}/>}
              <LoginOrRegistration
                current={current} 
                onClick={this.changeState.bind(this)}
              />
            </div>
          </div>
        )}
      </div>
    )
  }
}

const LoginOrRegistration = props => {
  return (
    <div className="toggle-register-login" onClick={props.onClick}>
        <a href="#/">{props.current}</a>
    </div>
  )
}
const mapStateToProps = ({ loading, authInfo }) => ({
  loading,
  authInfo
})

export default connect(mapStateToProps)(LoginPage);