import React from 'react';
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';

import UpdatePassWordForm from '../updatePassword/updatePasswordForm';

import { AlertMessage } from '../alertMessage/alertMessage';
import { displayAlert, resetAlert } from '../../actions';

class UpdatePasswordPage extends React.Component {

  componentDidMount() {
    this.props.history.listen(() => {
      this.props.resetAlert()
    })
  }

  renderAlertMessage() {
    const { serverResponse } = this.props.authInfo;
    if (serverResponse.status === 'error') {
      return <AlertMessage typeAlert={serverResponse.status} message={serverResponse.errorMessage} />

    } else if (serverResponse.status === 'success') {
      return <AlertMessage typeAlert={serverResponse.status} message={'Profile Updated!'} />
    }
  }

  render() {
    return (
      <>
        {this.props.loading.page ? (
          <div className="react-spinner-container"><ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105} /></div>
        ) : (
          <div id="update-password" className="login">
            <div className="container">
              {this.renderAlertMessage()}
              <UpdatePassWordForm />
            </div>
          </div>
        )}
      </>
    )
  }
}

const mapStateToProps = ({ loading, authInfo }) => ({
  loading,
  authInfo
})

const mapDispatchToProps = {
  displayAlert,
  resetAlert
}

export default connect(mapStateToProps, mapDispatchToProps)(UpdatePasswordPage)