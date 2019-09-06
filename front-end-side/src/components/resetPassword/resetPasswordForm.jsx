import React from 'react';
import { connect } from 'react-redux';
import { withRouter, Link } from 'react-router-dom';

import loginImg from '../../login.svg';
import { resetPassword } from '../../actions';


class ResetPasswordForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email_address: ''
    }
  }

  handleSubmit = event => {
    event.preventDefault();
    const { email_address } = this.state;
    const { history } = this.props;
    console.log('submitted!');
    const objPayload = {
      email_address,
      history
    }
    this.props.resetPassword(objPayload)
  }

  handleInputChange = event => {
    const targetName = event.target.name;
    this.setState({
      [targetName]: event.target.value
    })
  }

  render() {
    const { email_address } = this.state;
    return (
      <div className="base-container" ref={this.props.containerRef}>
        <div className="header">Reset Password</div> 
        <div className="content">
          <div className="image">
            <img src={loginImg} alt="login" />
            <form onSubmit={this.handleSubmit} className="form">
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input 
                  type="email" 
                  name="email_address" 
                  value={email_address}
                  onChange={this.handleInputChange} 
                  required
                />
              </div>
            <div className="footer">
              <button type="submit" className="btn">Submit</button>
              <Link to="/login">Cancel</Link>
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
  resetPassword
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(ResetPasswordForm))