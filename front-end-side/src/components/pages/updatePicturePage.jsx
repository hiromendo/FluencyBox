import React from 'react';
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';

import UpdatePictureForm from '../updatePicture/updatePictureForm';

import { AlertMessage } from '../alertMessage/alertMessage';
import { displayAlert, resetAlert } from '../../actions';

class UpdatePicturePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      password: '',
      confirmPassword: ''
    }
  }

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
      return <AlertMessage typeAlert={serverResponse.status} message={serverResponse.successMessage} />
    }
  }

  render() {
    return (
      <>
        {this.props.loading ? (
          <div className="react-spinner-container"><ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105} /></div>
        ) : (
          <div id="update-picture" className="login">
            <div className="container">
              {this.renderAlertMessage()}
              <UpdatePictureForm />
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

export default connect(mapStateToProps, mapDispatchToProps)(UpdatePicturePage)