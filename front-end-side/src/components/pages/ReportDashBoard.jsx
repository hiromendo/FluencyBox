import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';


import { getAllReports } from '../../actions';
import './ReportDashBoard.scss'

class ReportDashBoard extends Component {

  state = {
    isDoneLoading: false
  }

  componentDidMount() {
    const { serverResponse: { user }} = this.props.authInfo;
    this.props.getAllReports(user.uid)
  }

  renderReportsTable() {
    const { reports } = this.props.reportsStatus;
    reports.forEach( report => {
      console.log(report, 'this is report')
    })
    // let 
    return (
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Uploaded</th>
            <th>Score</th>
            <th>Genre</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Body content 1</td>
            <td>Body content 2</td>
            <td>Body content 3</td>
            <td>Body content 4</td>
          </tr>
          <tr>
            <td>Body Kenzo 1</td>
            <td>Body Kenzo 2</td>
            <td>Body Kenzo 3</td>
            <td>Body Kenzo 4</td>
          </tr>
        </tbody>
      </table>
    )
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
      this.renderReportsTable()
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