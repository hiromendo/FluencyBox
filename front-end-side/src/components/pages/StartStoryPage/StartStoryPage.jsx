import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';
import { connect } from 'react-redux';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMicrophone } from '@fortawesome/free-solid-svg-icons'

import { getStoryStarted, removeStoryContents, resetStoryStatus, pauseAudio } from '../../../actions';
import ContentScreen from './components/ContentScreen';
import './StartStoryPage.scss';

//TODO: Handle this more gracefully...
if (!('webkitSpeechRecognition' in window)) {
  console.error('does not support API')
}
let SpeechRecognition
SpeechRecognition = SpeechRecognition || window.webkitSpeechRecognition
const recognition = new SpeechRecognition()

recognition.continous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

// let mediaRecorder;


class StartStoryPage extends React.Component {
  /* https://www.robinwieruch.de/react-warning-cant-call-setstate-on-an-unmounted-component */
  _isMounted = false;
  constructor(props) {
    super(props);
    this.displayDesktopLayout = this.displayDesktopLayout.bind(this);
    this.displayMobileLayOut = this.displayMobileLayOut.bind(this);
    this.handleAudioStatus = this.handleAudioStatus.bind(this);
    this.updateAudioStatus = this.updateAudioStatus.bind(this);
    this.handleShowSubtitleDialog = this.handleShowSubtitleDialog.bind(this);
    this.toggleListenSpeechToText = this.toggleListenSpeechToText.bind(this);
    this.handleListen = this.handleListen.bind(this);
    this.handleAudioRecording = this.handleAudioRecording.bind(this);
    this.state = {
      isMobile: false,
      showSubtitle: false,
      audioStatus: 'initial',
      isDisplayContentImage: false,
      micPermissionStatus: null,
      isReadyToRecord: false,
      listeningText: false,
      mediaStreamObj: null,
      mediaRecorder: null,
      audioFile: null
    }
    this.constraintObj = {
      audio: true 
    }
    this.audioNode = new Audio();
    this.stream = '';

  }
  

  /*TODO: there should be a spinning gif here to indicate the story is being loaded */
  async componentDidMount() {
    this._isMounted = true;
    const { storyContent } = this.props;
    if (storyContent.isContentFinishedLoaded === false) {
      const { authInfo: { serverResponse: { user }}, uid, routeProps: { history } } = this.props;
      const payloadObj = {
        user_uid: user.uid,
        history,
        story_uid: uid
      }
      this.props.getStoryStarted(payloadObj)
    }

    try {
      const mediaStreamObj = await navigator.mediaDevices.getUserMedia(this.constraintObj)
      if (this._isMounted) {
        this.setState({
          micPermissionStatus: true,
          mediaStreamObj
        }, () => {
          this.handleAudioRecording();
        })
      }
    } catch(error) {
      console.error(error)
      console.error('User has blocked microphone permission');
      if (this._isMounted) {
        this.setState({
          micPermissionStatus: false
        })
      }
    }
    
  }
    
  componentWillUnmount() {
    this._isMounted = false;
    if (this.stream) {
      this.stream.getTracks()
      .forEach((track) => track.stop());
    }
    this.audioNode.pause()
    this.props.removeStoryContents();
    this.props.resetStoryStatus();
  }
  
  throttledHandleWindowResize = () => {
    //TODO: add a throttle here for optimzation purpose
    this.setState({ isMobile: window.innerWidth < 768 })
  }

  //TODO: add try/catch error handling here when loading audio file
  handleAudioStatus() {
    if (!this.state.micPermissionStatus) return
    if (this.state.audioStatus === 'playing') {
      this.setState({
        audioStatus: 'paused'
      }, () => {
        this.audioNode.pause()
      })
    } else if (this.state.audioStatus === 'paused') {
      this.setState({
        audioStatus: 'playing'
      }, () => {
        this.audioNode.play()
      })
    } else if (this.state.audioStatus === 'repeat') {
      this.audioNode.currentTime = 0;
      this.audioNode.play();
      this.setState({
        audioStatus: 'playing'
      })
    } else {
      this.setState({
        audioStatus: 'playing',
        isDisplayContentImage: true
      }, () => {
        this.audioNode.src = this.props.storyContent.scene.story_scene_speakers[0].audio_url;
        this.audioNode.play()
        this.audioNode.addEventListener("ended", () => {
          this.setState({
            audioStatus: 'finished',
            isReadyToRecord: true
          })
        })
      })
    }
  }

  updateAudioStatus(newAudioState) {
    if (this.state.audioStatus === 'initial') return
    this.setState({
      audioStatus: newAudioState
    }, () => {
      this.handleAudioStatus()
    })
  }

  handleShowSubtitleDialog() {
    this.setState({
      showSubtitle: !this.state.showSubtitle
    })
  }

  toggleListenSpeechToText() {
    this.setState({
      listeningText: !this.state.listeningText
    }, this.handleListen)
  }

  handleListen() {
    console.log('listening?', this.state.listeningText)
    if (this.state.listeningText) {
      recognition.start()
      recognition.onend = () => {
        recognition.start()
      } 
      this.state.mediaRecorder.start()
    
    } else {
      recognition.stop();
      recognition.onend = () => { 
        console.log('I stopped listening')
      }
      this.state.mediaRecorder.stop()
    }

    recognition.onstart = () => {
      console.log("Listening!")
    }

    recognition.onerror = event => {
      console.log("Error occurred in recognition: " + event.error)
    }

    let finalTranscript = ''
    recognition.onresult = event => {
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalTranscript += transcript + ' ';
        else interimTranscript += transcript;
      }
      document.querySelector('#speech-to-text span.word-texts').innerHTML = interimTranscript
      document.querySelector('#speech-to-text span.word-texts').innerHTML = finalTranscript
    }
  }

  handleAudioRecording() {
    if (!this.state.mediaStreamObj) return
    const mediaRecorder = new MediaRecorder(this.state.mediaStreamObj);
    let chunks = [];

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) {
        chunks.push(e.data)
      }
    }

    mediaRecorder.onstop = () => {
      if (chunks && chunks.length > 0) {
        const audio = document.querySelector('.sound-clips');
        audio.controls = true;
        const blob = new Blob(chunks, { type: 'audio/mpeg-3' });
        const audioURL = window.URL.createObjectURL(blob);
        audio.src = audioURL;
        chunks = [];

        let audioFile = new File([blob], 'sample-audio.mp3', {
          type: 'audio/mp3'
        });

        this.setState({
          audioFile
        })

        audio.play()
      }
    }

    this.setState({ mediaRecorder: mediaRecorder });
  }

  displayDesktopLayout() {
    const { uid } = this.props
    return (
      <Grid>
        <Row middle="md">
          <Col md={3} mdOffset={1}>
            <div className="btn btn-dark-blue" onClick={() => this.updateAudioStatus('repeat')}>Repeat Audio</div>
          </Col>
          <Col md={4} mdOffset={1}>
            <div className={`btn btn-dark-blue ${this.state.showSubtitle ? 'btn-dark-blue-active' : ''}`} onClick={this.handleShowSubtitleDialog}>Hide Subtitles</div>
          </Col>
          <Col md={1}>
            <div className={"btn btn-dark-blue"}>Restart</div>
          </Col>
          <Col md={1}>
            <div className="btn btn-dark-blue">
              <Link to={`/story/${uid}`}>Home</Link>
            </div>
          </Col>
        </Row>
        <Row center="md">
          <Col md={12}>
            <ContentScreen 
              isDisplayContentImage={this.state.isDisplayContentImage}
              showSubtitle={this.state.showSubtitle}
              micPermissionStatus={this.state.micPermissionStatus}
              handleAudioStatus={this.handleAudioStatus} 
              storyContent={this.props.storyContent} />
          </Col>
        </Row>
        <Row>
          <Col md={3} mdOffset={1}>
          <div className="btn btn-dark-blue">
            Record Again
          </div>
          </Col>
          <Col md={2} mdOffset={1}>
            <div onClick={this.toggleListenSpeechToText} id="btnStartRecord" className="btn btn-dark-blue">
              Record Button
            </div>
          </Col>
          <Col md={3} mdOffset={2}>
            <div className="btn btn-dark-blue">
              Next Scene
            </div>
          </Col>
        </Row>
        <Row>
          <div id="speech-to-text">
            <FontAwesomeIcon icon={faMicrophone} color="green" />
            <span className="word-texts"></span>
          </div>
        </Row>
        <Row>
          <audio className="sound-clips"></audio>
        </Row>
      </Grid>
    )
  }

  displayMobileLayOut() {
    const { uid } = this.props;
    return (
      <Grid>
        <Row middle="xs">
          <Col xs={4} xsOffset={1}>
            <div className="btn btn-dark-blue">Repeat Audio</div>
          </Col>
          <Col xs={4} xsOffset={2}>
            <div className="btn btn-dark-blue">Hide Subtitles</div>
          </Col>
        </Row>
        <Row center="xs">
          <Col xs={12}>
            <div id="story-content">Content Here</div>
          </Col>
        </Row>
        <Row center="xs" middle="xs">
          <Col xs={3}>
            <div className="btn btn-dark-blue">Restart</div>
          </Col>
          <Col xs={4} xsOffset={1}>
            Record Button
          </Col>
          <Col xs={3} xsOffset={1}>
          <div className="btn btn-dark-blue">
            <Link to={`/story/${uid}`}>Home</Link>
          </div>
          </Col>
        </Row>
      </Grid>
    )
  }

  render() {
    return (
      <div id="story-media">
        {this.state.isMobile ? this.displayMobileLayOut() : this.displayDesktopLayout()}
      </div>
    )
  }
}

const mapStateToProps = ({ storiesInfo, authInfo, storyContent, storyStatus }) => ({
  storiesInfo,
  authInfo,
  storyContent,
  storyStatus
})

const mapDispatchToProps = {
  getStoryStarted,
  removeStoryContents,
  resetStoryStatus,
  pauseAudio
}


export default connect(mapStateToProps, mapDispatchToProps)(StartStoryPage);