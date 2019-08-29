import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';
import { sendRegister, cacheRegisterInfo } from '../../actions';
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
    // this.generateRandomID()
    const { registerCache } = this.props
    this.setState(prevState => {
      return registerCache
    })
  }

  /* Dev purpose only */
  generateRandomID = () => {
    const c = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    const randomID = Array.from({length:4}, _ => c[Math.floor(Math.random()*c.length)]).join('')
    this.setState({
      userName: randomID,
      email: `${randomID}@gmail.com`
    })
  }

  handleSubmit = event => {
    event.preventDefault();
    const { firstname, lastname, userName, password, phone, email, confirmPassword } = this.state;
    const { history } = this.props;
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
      this.props.cacheRegisterInfo(this.state)
      this.props.sendRegister(userInfo, history);
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
    const { firstname, lastname, userName, password, phone, email, confirmPassword } = this.state;

    return (
      <div className="base-container" ref={this.props.containerRef}>
        <div className="header">Register</div> 
        <div className="content">
          <div className="image">
            <form onSubmit={this.handleSubmit} className="form">
              <div className="form-group">
                <label htmlFor="firstname">First Name</label>
                <input 
                  type="text" 
                  name="firstname" 
                  value={firstname}
                  onChange={this.handleInputChange} 
                  required
              />
              </div>
              <div className="form-group">
                <label htmlFor="lastname">Last Name</label>
                <input 
                  type="text" 
                  name="lastname" 
                  value={lastname}
                  onChange={this.handleInputChange} 
                  required
              />
              </div>
              <div className="form-group">
                <label htmlFor="userName">User Name</label>
                <input 
                  type="text" 
                  name="userName" 
                  value={userName}
                  onChange={this.handleInputChange} 
                  required
              />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input 
                  type="email" 
                  name="email" 
                  value={email}
                  onChange={this.handleInputChange} 
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input 
                  type="tel" 
                  name="phone"
                  value={phone}
                  onChange={this.handleInputChange} 
                  placeholder='Optional'
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
              <button type="submit" className="btn">Register</button>
            </div>
            </form>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ loading, registerCache }) => ({
  loading,
  registerCache
})

const mapDispatchToProps = {
  sendRegister,
  cacheRegisterInfo
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Register))