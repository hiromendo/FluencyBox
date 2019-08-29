import React from 'react';
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';

import Login from '../login/login';
import Register from '../login/register';

import { AlertMessage } from '../alertMessage/alertMessage';
import { displayAlert } from '../../actions';

import './loginPage.scss'

class LoginPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLogginActive: true,
      redirectToReferrer: false
    }
  }

  changeState() {
    this.props.displayAlert(null, null)
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
      <>
        {this.props.loading ? (
          <div className="react-spinner-container"><ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105} /></div>
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
      </>
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

const mapDispatchToProps = {
  displayAlert
}

export default connect(mapStateToProps, mapDispatchToProps)(LoginPage);