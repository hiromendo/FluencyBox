import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { resetAlert, updatePassword } from '../../actions';

class UpdatePassWordForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPassword: '',
      password: '',
      confirmPassword: ''
    }
  }

  handleSubmit = event => {
    event.preventDefault();
    const { password, confirmPassword, currentPassword } = this.state;
    const { serverResponse: { user } } = this.props.authInfo;
    const isPasswordMatched = this.validatePassword();

    if (isPasswordMatched) {
      const payload = {
        currentPassword,
        password,
        confirmPassword,
        uid: user.uid
      }
      this.props.updatePassword(payload)

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

  render() {
    const { currentPassword, password, confirmPassword } = this.state;
    return (
      <div className="base-container" ref={this.props.containerRef}>
        <h2 className="header">Update Password</h2> 
        <div className="content">

          <form onSubmit={this.handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="currentPassword">Current Password</label>
              <input 
                type="password" 
                name="currentPassword"
                ref="currentPasswordNode"
                value={currentPassword}
                pattern=".{8,}"
                onChange={this.handleInputChange} 
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password <span>8 minimum characters</span></label>
              <input 
                type="password" 
                name="password"
                ref="passwordNode"
                value={password}
                title="8 characters minimum"
                pattern=".{8,}"
                onChange={this.handleInputChange} 
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input 
                type="password" 
                name="confirmPassword"
                ref="confirmPasswordNode"
                value={confirmPassword}
                title="8 characters minimum"
                pattern=".{8,}"
                onChange={this.handleInputChange} 
                required
              />
            </div>
            <div className="footer">
              <button type="submit" className="btn btn-green">Update</button>
              <Link className="cancel" to="/userprofile">Cancel</Link>
            </div>
          </form>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ loading, authInfo }) => ({
  loading,
  authInfo
})

const mapDispatchToProps = {
  resetAlert,
  updatePassword
}

export default connect(mapStateToProps, mapDispatchToProps)(UpdatePassWordForm)