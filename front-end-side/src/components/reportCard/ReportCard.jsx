import React, { Component } from 'react'
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faVolumeUp } from '@fortawesome/free-solid-svg-icons'
import { getReportContents, resetReportContents } from '../../actions';
import './ReportCard.scss' 
import './assets/blue-speaker.svg'
import BlueSpeakerSVG from './assets/blue-speaker'

class ReportCard extends Component {
  
  async componentDidMount() {
    const { authInfo: { serverResponse: { user }}, reportContent, uid } = this.props;
    if (reportContent.isReportContentFinishedLoaded === false) {
      const payloadObj ={
        user_uid: user.uid,
        report_uid: uid
      }
      await this.props.getReportContents(payloadObj)
      this.onlyPlayOneIn(document.body)
    }
  }

  componentWillUnmount() {
    const container = document.body;
    container.removeEventListener('play', this.onlyPlayOneIn);
    const audio_elements = container.getElementsByTagName('audio');
    Array.from(audio_elements).forEach( audio => audio.pause())
    this.props.resetReportContents()
  }

  onlyPlayOneIn(container) {
    container.addEventListener('play', event => {
    const audio_elements = container.getElementsByTagName('audio')
      for(let i=0; i < audio_elements.length; i++) {
        let audio_element = audio_elements[i];
        let svgIcon = audio_element.nextSibling;
        if (audio_element !== event.target) {
          audio_element.pause();
          svgIcon.classList.remove('playing-audio')
          audio_element.removeEventListener('playing', this.handleAddingPlayingClassName)
          audio_element.removeEventListener('ended', this.handleRemovingPlayingClassName)
          audio_element.currentTime = 0;
        }
      }
    }, true);

  }

  renderPromptDialogs(promptDialogs) {
    const result = promptDialogs.map((audioInfo, idx) => {
      return (
        <React.Fragment key={`${audioInfo.order}-${idx}`}>
          <div className="prompt-bubble prompt-text">
            {audioInfo.audio_text}
          </div>
          <audio id={`${audioInfo.order}-speaker-audio`} src={audioInfo.audio_filename}></audio>
          <FontAwesomeIcon className="prompt-icon-speaker" icon={faVolumeUp} color="#b7b7b7" onClick={() => this.handleAudioPlayBack(`${audioInfo.order}-speaker-audio`)} />
          </React.Fragment>
      )
    })
    return result;
  }

  handleDisplayingAudioPlayBacks() {
    const { reportContent: { report_details } } = this.props;
    const result = report_details.report_images.map((packet, idx) => {
      console.log(packet, 'this is packet')
      return (
        <React.Fragment key={`${packet.scene_number}-${idx}`}>
          <div className="scene-number">{packet.scene_number}</div>
          {/* this is for the main prompt playback */}
          <div className="prompt-container">
            {this.renderPromptDialogs(packet.story_scene_speakers)}
          </div>
          {/* ****************** */}
          {/* This is for master and user response */}
          <div className="prompt-container user-response">
            <audio id={`${packet.scene_number}-master-audio`} className="master-prompt-text" src={packet.master_audio_url}></audio>
            <FontAwesomeIcon className="prompt-icon-speaker" icon={faVolumeUp} color="#b7b7b7" onClick={() => this.handleAudioPlayBack(`${packet.scene_number}-master-audio`)} />

            <audio id={`${packet.scene_number}-user-response-audio`} className="user-prompt-text" src={packet.user_response_audio_url}></audio>
            <FontAwesomeIcon className="prompt-icon-speaker user-response-speaker" icon={faVolumeUp} color="#1762A7" onClick={() => this.handleAudioPlayBack(`${packet.scene_number}-user-response-audio`)} />

            {/* <BlueSpeakerSVG />  */}

            <div className="prompt-bubble master-prompt-text hide-bubble">
              {packet.master_response_text}
            </div>
            <div className="prompt-bubble user-prompt-text">
              {packet.user_response_audio_text}
            </div>
          {/* ****************** */}
          </div>
          <div className="img-report-container">
              <img src={packet.report_image_url_rhythm} alt="rhythm" />
              <img src={packet.report_image_url_stress} alt="tension" />
            </div>
        </React.Fragment>
      )
    })

    return result;
  }

  handleAddingPlayingClassName(event) {
    const svgIcon = event.target.nextSibling
    svgIcon.classList.add('playing-audio');

    let bubbleType = event.target.classList[0];
    if (bubbleType) {
      event.target.parentElement.querySelector(`div.${bubbleType}`).classList.remove('hide-bubble')
      event.target.parentElement.querySelector(`div:not(.${bubbleType})`).classList.add('hide-bubble')
    }
  }

  handleRemovingPlayingClassName(event) {
    const svgIcon = event.target.nextSibling
    svgIcon.classList.remove('playing-audio')
  }

  handleAudioPlayBack(idElement) {
    const audioNode = document.getElementById(idElement);
    audioNode.play()

    audioNode.addEventListener('playing', this.handleAddingPlayingClassName)

    audioNode.addEventListener('ended', this.handleRemovingPlayingClassName)
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
        <div className="page-report">
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