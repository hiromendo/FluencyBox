import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';


import { getAllReports } from '../../actions';

class ReportDashBoard extends Component {

  state = {
    isDoneLoading: false
  }

  componentDidMount() {
    const { serverResponse: { user }} = this.props.authInfo;
    this.props.getAllReports(user.uid)
  }

  render() {
    const { isFetchingReports } = this.props.reportsStatus
    if (isFetchingReports) {
      return (
        <div className="react-spinner-container ">
          <ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105}  />
        </div>
      )
    }
    return (
      <div>
        Hey you
      </div>
    )
  }
}

const mapStateToProps = ({ reportsStatus, authInfo }) => ({
  reportsStatus,
  authInfo
})

const mapDispatchToProps = {
  getAllReports
}

export default connect(mapStateToProps, mapDispatchToProps)(ReportDashBoard)