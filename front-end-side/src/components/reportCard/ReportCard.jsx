import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';

import { getReportContents, resetReportContents } from '../../actions';

class ReportCard extends Component {
  
  async componentDidMount() {
    const { authInfo: { serverResponse: { user }}, reportContent, uid } = this.props;
    if (reportContent.isReportContentFinishedLoaded === false) {
      const payloadObj ={
        user_uid: user.uid,
        report_uid: uid
      }
      await this.props.getReportContents(payloadObj)
    }
  }

  componentWillUnmount() {
    this.props.resetReportContents()
  }

  render() {
    const { reportContent } = this.props;
    if (!reportContent.isReportContentFinishedLoaded) {
      return (
        <div className="react-spinner-container ">
          <ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105}  />
        </div>
      )
    }
    const { report_details } = reportContent
    return (
      <div className="page">
        <h1>{report_details.name}</h1>
        <br />
        <h2>{report_details.score}</h2>
      </div>
    )
  }
}

const mapStateToProps = ({ authInfo, reportContent }) => ({
  authInfo,
  reportContent
})

const mapDispatchToProps = {
  getReportContents,
  resetReportContents
}


export default connect(mapStateToProps, mapDispatchToProps)(ReportCard)