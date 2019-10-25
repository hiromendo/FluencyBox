import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';
import { connect } from 'react-redux';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMicrophone } from '@fortawesome/free-solid-svg-icons'

import { getStoryStarted, removeStoryContents, resetStoryStatus, pauseAudio, getAsyncNextScene, getStoryContents, completeStory } from '../../../actions';
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

class StartStoryPage extends React.Component {
  /* https://www.robinwieruch.de/react-warning-cant-call-setstate-on-an-unmounted-component */
  _isMounted = false;
  constructor(props) {
    super(props);
    this.displayDesktopLayout = this.displayDesktopLayout.bind(this);
    this.displayMobileLayOut = this.displayMobileLayOut.bind(this);
    this.handleContentAudioStatus = this.handleContentAudioStatus.bind(this);
    this.updateAudioStatus = this.updateAudioStatus.bind(this);
    this.handleShowSubtitleDialog = this.handleShowSubtitleDialog.bind(this);
    this.toggleListenSpeechToText = this.toggleListenSpeechToText.bind(this);
    this.handleListen = this.handleListen.bind(this);
    this.handleAudioRecording = this.handleAudioRecording.bind(this);
    this.handleAnalyzingsTextForNextScene = this.handleAnalyzingsTextForNextScene.bind(this);
    this.handleButtonNextScene = this.handleButtonNextScene.bind(this);
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
      audioFile: null,
      requestNextSceneOrder: null
    }
    this.constraintObj = {
      audio: true 
    }
    this.audioNode = new Audio();
    this.stream = '';

    this.wordTexts = React.createRef()
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
  handleContentAudioStatus() {
    if (!this.state.micPermissionStatus) return
    if (this.state.audioStatus === 'playing') {
      this.setState({
        audioStatus: 'paused',
        isReadyToRecord: false
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
        audioStatus: 'playing',
        isReadyToRecord: false
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
      this.handleContentAudioStatus()
    })
  }

  handleShowSubtitleDialog() {
    this.setState({
      showSubtitle: !this.state.showSubtitle
    })
  }

  toggleListenSpeechToText() {
    const { storyContent: { scene } } = this.props;
    const keywords = scene.scene_keywords;
    if (!this.state.isReadyToRecord) return
    if (!keywords.length) return 
    this.setState({
      listeningText: !this.state.listeningText
    }, this.handleListen)
  }

  handleListen() {
    if (this.state.listeningText) {
      this.wordTexts.current.innerText = '';
      recognition.start()
      recognition.onend = () => {
        recognition.start()
      } 
      this.state.mediaRecorder.start()
    
    } else {
      recognition.stop();

      recognition.onend = () => { 
        console.log('I stopped listening')
        this.handleAnalyzingsTextForNextScene()
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
      this.wordTexts.current.innerText = interimTranscript
      this.wordTexts.current.innerText = finalTranscript
    }
  }

  handleAudioRecording() {
    const { authInfo: { serverResponse: { user }}, storyContent: { scene }} = this.props
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

        let audioFile = new File([blob], `${user.first_name}-${user.uid}-${scene.uid}.mp3`, {
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

  handleAnalyzingsTextForNextScene() {
    const { scene: { scene_keywords, order } } = this.props.storyContent
    const textValue = this.wordTexts.current.innerText;
    let correctIdx;
    scene_keywords.some((x, idx) => {
      if (textValue.includes(x.keyword)) {
        correctIdx = idx;
        return true
      }
    })

    if ((correctIdx >= 0) && scene_keywords[correctIdx].next_scene_order === order) {
      console.log('repeat the scene')
    } else if (correctIdx >= 0) {
      this.setState({
        requestNextSceneOrder: scene_keywords[correctIdx].next_scene_order
      })
      console.log('make an HTTP call')
    } else {
      console.log('no words found matching')
    }
  }

  handleButtonNextScene() {
    const { requestNextSceneOrder } = this.state;
    const { storyContent, storyStatus } = this.props
    const keywords = storyContent.scene.scene_keywords;
    if (keywords.length) {
      const textValue = this.wordTexts.current.innerText;
      const data = new FormData();
      data.append('user_story_uid', storyStatus.userStoryID);
      data.append('user_audio', this.state.audioFile);
      data.append('audio_text', textValue);
      data.append('story_scene_speaker_id', storyContent.scene.story_scene_speakers[0].id);
      data.append('next_scene_order', requestNextSceneOrder);
  
      this.props.getAsyncNextScene(data)
    } else if (!keywords.length && storyContent.scene.next_scene_order)  {
      //if there is no keywords but theres next scene, move on to next scene provided by server response
      const objPayload = {
        next_scene_order: storyContent.scene.next_scene_order,
        story_uid: storyContent.scene.uid,
        user_story_uid: storyStatus.userStoryID
      }
      this.props.getStoryContents(objPayload)
    } else {
      console.log('the end')
      const objPayload = {
        user_story_uid: storyStatus.userStoryID
      }
      this.props.completeStory(objPayload)
    }
  }

  displayDesktopLayout() {
    const { uid } = this.props
    const { listeningText } = this.state
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
              handleContentAudioStatus={this.handleContentAudioStatus} 
              storyContent={this.props.storyContent} />
          </Col>
        </Row>

        <div className="btn-container">
          <div className="btn">
            <button onClick={this.toggleListenSpeechToText} id="btnStartRecord" className={`btn-record ${listeningText ? 'Rec' : 'notRec'}`}>
              Record Button
            </button>
          </div>
          <div onClick={this.handleButtonNextScene} className="btn btn-dark-blue">Next Scene</div>
        </div>
        <Row>
          <div id="speech-to-text">
            <FontAwesomeIcon icon={faMicrophone} color="green" />
            <span ref={this.wordTexts} className="word-texts"></span>
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

const mapStateToProps = ({ authInfo, storiesInfo, storyContent, storyStatus }) => ({
  authInfo,
  storiesInfo,
  storyContent,
  storyStatus
})

const mapDispatchToProps = {
  getStoryStarted,
  removeStoryContents,
  resetStoryStatus,
  pauseAudio,
  getAsyncNextScene,
  getStoryContents,
  completeStory
}


export default connect(mapStateToProps, mapDispatchToProps)(StartStoryPage);