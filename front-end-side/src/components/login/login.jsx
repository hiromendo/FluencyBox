import React from 'react';
import { connect } from 'react-redux';
import { withRouter, Link } from 'react-router-dom';

import loginImg from '../../login.svg';
import { getLogin } from '../../actions';
import "./style.scss";

export class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      userName : '',
      password: ''
    }
  }

  handleSubmit = event => {
    event.preventDefault();
    const { userName, password } = this.state;
    const userInfo = { userName, password };
    const { history } = this.props;

    this.props.getLogin(userInfo, history);
  }

  handleInputChange = event => {
    const targetName = event.target.name;
    this.setState({
      [targetName]: event.target.value
    })
  }

  render() {
    const { userName, password } = this.state;
    return (
      <div className="base-container" ref={this.props.containerRef}>
        <div className="content">
          <div className="header">Sign In</div> 
          <form onSubmit={this.handleSubmit} className="form">
            <div className="form-group">
              <input 
                type="text" 
                name="userName"
                placeholder="email"
                value={userName} 
                onChange={this.handleInputChange} 
                required
              />
            </div>
            <div className="form-group">
              <input 
                type="password" 
                name="password"
                placeholder="password"
                value={password} 
                onChange={this.handleInputChange} 
                required
              />
            </div>
            <div className="footer">
              <button type="submit" className="btn btn-large btn-orange">Sign In</button>
            </div>
            <Link className="reset-password" to="/resetpassword">Forgot Password?</Link>
          </form>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ loading }) => ({
  loading
})

const mapDispatchToProps = {
  getLogin
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Login))