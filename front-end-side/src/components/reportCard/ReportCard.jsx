import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faVolumeUp } from '@fortawesome/free-solid-svg-icons'
import { getReportContents, resetReportContents } from '../../actions';
import './ReportCard.scss'

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

  handleDisplayingAudioPlayBacks() {
    const { reportContent: { report_details } } = this.props;
    const result = report_details.report_images.map((packet, idx) => {
      console.log(packet, 'this is packet')
      return (
        <React.Fragment key={`${packet.scene_number}-${idx}`}>
          <div className="prompt-text">
            {packet.speaker_audio_text}
          </div>
          <FontAwesomeIcon className="prompt-icon-speaker" icon={faVolumeUp} color="#b7b7b7" />
        </React.Fragment>
      )
    })
    
    return (
      <div className="prompt-container">
        {result}
      </div>

    )
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
    const { report_details } = reportContent;
    return (
      <div className="page">
        <div className="row-info">
          <div className="column">
            <div>{report_details.name} </div>
            <div>Total Score: {report_details.score}</div>
          </div>
          <div className="column">
            <div>Show all Scores</div>
            <div>Show Bottom Scores</div>
          </div>
        </div>
        <div>
          {this.handleDisplayingAudioPlayBacks()}
        </div>
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