import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { resetAlert, updateProfilePicture, displayErrorUpdate } from '../../actions';

class UpdatePictureForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedFilestate: null,
      imagePreview: null,
      errorMessage: ''
    }
  }

  handleSubmit = event => {
    event.preventDefault();
    const { serverResponse: { user } } = this.props.authInfo;
    const data = new FormData();
    data.append('profile_picture', this.state.selectedFilestate);

    const payload = {
      data,
      uid: user.uid
    }

    this.props.updateProfilePicture(payload);
  }

  checkMimeType = event => {
    let files = event.target.files;
    let err = '';
    const types = ['image/png', 'image/jpeg', 'image/gif'];
    for(var x = 0; x<files.length; x++) { 
      if (types.every(type => files[x].type !== type)) { 
        err += files[x].type+' is not a supported format\n';
      }
    }
    if (err !== '') {
      event.target.value = null;
      this.setState({ errorMessage: err });
      console.error(err) ;
      const payload = {
        errorMessage: err,
        status: 'error'
      }
      this.props.displayErrorUpdate(payload)
      return false;
    } 
    return true;
  }

  onChangeHandler = event => {
    this.props.resetAlert()
    const isFilePicture = this.checkMimeType(event);
    if (isFilePicture) {
      this.setState({
        selectedFilestate: event.target.files[0],
        imagePreview: URL.createObjectURL(event.target.files[0])
      })
    }
  }


  render() {
    const { imagePreview } = this.state;
    return (
      <div className="base-container" ref={this.props.containerRef}>
        <div className="header">Update Profile Picture</div> 
        <div className="content">

          <form onSubmit={this.handleSubmit} className="form">
            <div className="form-group">
              <div>
                {/* <label htmlFor="Profile Picture">Profile Picture</label> */}
                {imagePreview ? null : <input type="file" name="file" onChange={this.onChangeHandler}/>} 
                {imagePreview ? <img className="preview-upload" src={imagePreview} alt="preview"/> : null }
              </div>
            </div>
            <div className="footer">
              <button type="submit" className="btn btn-green">Upload</button>
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
  updateProfilePicture,
  displayErrorUpdate
}

export default connect(mapStateToProps, mapDispatchToProps)(UpdatePictureForm)