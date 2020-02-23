import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';
import { Link } from 'react-router-dom';

import { getAllReports } from '../../actions';
import './ReportDashBoard.scss'

class ReportDashBoard extends Component {

  renderReportsTable() {
    const { reports } = this.props.reportsStatus;
    let rows = [];
    reports.forEach( (report, idx) => {
      let cells = [];
      cells.push(
        <td 
          key={`${report.uid}-${report.name}`}>
            <Link className="report-link" to={`/report/${report.uid}`}>
              {report.name}
            </Link>
        </td>
      )

      cells.push(<td key={`${report.uid}-${report.uploaded_at}`}>{report.uploaded_at}</td>)
      cells.push(<td key={`${report.uid}-${report.score}`}>{report.score}/100</td>)
      cells.push(<td key={`${report.uid}-${report.genre}`}>{report.genre}</td>)
      rows.push(<tr key={`${report.uid}-${idx}`}>{cells}</tr>)
    })

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
          {rows}
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
      <div className="page">
        {this.renderReportsTable()}
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