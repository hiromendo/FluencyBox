import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import loginImg from '../../login.svg';
import { getLogin } from '../../actions';
import "./style.scss";

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      userName : 'test@msn.com',
      password: '12345678'
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
        <div className="header">Login</div> 
        <div className="content">
          <div className="image">
            <img src={loginImg} alt="login" />
            <form onSubmit={this.handleSubmit} className="form">
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
                <label htmlFor="password">Password</label>
                <input 
                  type="password" 
                  name="password" 
                  value={password} 
                  onChange={this.handleInputChange} 
                  required
                />
              </div>
            <div className="footer">
              <button type="submit" className="btn">Login</button>
            </div>
            </form>
          </div>
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