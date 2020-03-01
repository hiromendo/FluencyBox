import React from 'react';
import { connect } from 'react-redux';
import { withRouter, Link } from 'react-router-dom';
import { sendRegister, cacheRegisterInfo, updateUserInfo } from '../../actions';
import "./style.scss";

class Register extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      firstname: '',
      lastname: '',
      userName: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: ''
    }
  }

  componentDidMount() {
    const { registerCache, reUpdateInfoProfile, authInfo: { serverResponse : { user } } } = this.props;
    if (reUpdateInfoProfile) {
      const obj = {
        firstname: user.first_name,
        lastname: user.last_name,
        userName: user.user_name,
        email: user.email_address,
        phone: user.phone_number,
      };
      this.setState(() => {
        return obj
      })

    } else {
      this.setState(prevState => {
        return registerCache
      })

    }
  }

  handleSubmit = event => {
    event.preventDefault();
    const { firstname, lastname, userName, password, phone, email, confirmPassword } = this.state;
    const { history, reUpdateInfoProfile, authInfo: { serverResponse: { user } } } = this.props;
    this.props.cacheRegisterInfo(this.state)
    if (reUpdateInfoProfile) {

      const userInfo = {
        "first_name" : firstname,
        "last_name" : lastname,
        "user_name" : userName,
        "email_address" : email,
        "phone_number" : phone,
      }

      this.props.updateUserInfo(userInfo, user.uid, history)
  
    } else {
      const isPasswordMatched = this.validatePassword()
      if (isPasswordMatched) {
        const userInfo = {
          "first_name" : firstname,
          "last_name" : lastname,
          "user_name" : userName,
          "email_address" : email,
          "phone_number" : phone,
          "password" : password,
          "confirm_password": confirmPassword
        }
        this.props.sendRegister(userInfo, history);

      }
    }
  }

  handleInputChange = event => {
    const targetName = event.target.name;
    const passWordInputNode = this.refs.passwordNode
    const confirmPasswordInputNode = this.refs.confirmPasswordNode;
    if (targetName === 'confirmPassword' && event.target.value.length >= 8 && this.refs.passwordNode.value) {
      if (event.target.value !== passWordInputNode.value) {
        confirmPasswordInputNode.setCustomValidity('Password does not match')
      } else {
        confirmPasswordInputNode.setCustomValidity('')
      }
    }
    this.setState({
      [targetName]: event.target.value
    })
  }

  validatePassword() {
    const { password, confirmPassword } = this.state;
    if (password !== confirmPassword) {
      return false
    } else {
      return true
    }
  }

  renderPassWordInputs() {
    const { reUpdateInfoProfile } = this.props;
    const { password, confirmPassword } = this.state;
    if (!reUpdateInfoProfile) {
      return (
        <>
          <div className="form-group">
            <input 
              type="password" 
              name="password"
              ref="passwordNode"
              value={password}
              placeholder="password - 8 characters minimum"
              title="8 characters minimum"
              pattern=".{8,}"
              onChange={this.handleInputChange} 
              required
            />
          </div>
          <div className="form-group">
            <input 
              type="password" 
              name="confirmPassword"
              placeholder="confirm password"
              ref="confirmPasswordNode"
              value={confirmPassword}
              title="8 characters minimum"
              pattern=".{8,}"
              onChange={this.handleInputChange} 
              required
            />
          </div>
        </>
      )
    }
  }

  render() {
    const { userName, email } = this.state;
    const { reUpdateInfoProfile } = this.props;

    return (
      <div className="base-container" ref={this.props.containerRef}>
        <div className="content">
          <div className="header">{reUpdateInfoProfile ? 'Update Profile Info' : 'Sign Up'}</div> 
          <div>
            <form onSubmit={this.handleSubmit} className="form">
              <div className="form-group">
                <input 
                  type="text" 
                  name="userName"
                  placeholder="username"
                  value={userName}
                  onChange={this.handleInputChange} 
                  required
              />
              </div>
              <div className="form-group">
                <input 
                  type="email" 
                  name="email" 
                  placeholder="email"
                  value={email}
                  onChange={this.handleInputChange} 
                  required
                />
              </div>
              {this.renderPassWordInputs()}
              <div className="footer">
                <button type="submit" className="btn btn-large btn-orange">{reUpdateInfoProfile ? 'Update' : 'Sign Up'}</button>
                {reUpdateInfoProfile ? <Link className="cancel" to="/userprofile">Cancel</Link> : null }
              </div>
            </form>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ loading, registerCache, authInfo }) => ({
  loading,
  registerCache,
  authInfo
})

const mapDispatchToProps = {
  sendRegister,
  cacheRegisterInfo,
  updateUserInfo
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Register))