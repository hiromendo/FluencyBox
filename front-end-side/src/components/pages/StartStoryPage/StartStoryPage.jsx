import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMicrophone } from '@fortawesome/free-solid-svg-icons'
import ReactLoading from 'react-loading';

import { getStoryStarted, removeStoryContents, resetStoryStatus, getAsyncNextScene, getStoryContents, completeStory } from '../../../actions';
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

class StartStoryPage extends Component {
  /* https://www.robinwieruch.de/react-warning-cant-call-setstate-on-an-unmounted-component */
  _isMounted = false;
  constructor(props) {
    super(props);
    this.displayDesktopLayout = this.displayDesktopLayout.bind(this);
    this.handleContentAudioStatus = this.handleContentAudioStatus.bind(this);
    this.updateAudioStatus = this.updateAudioStatus.bind(this);
    this.handleShowSubtitleDialog = this.handleShowSubtitleDialog.bind(this);
    this.toggleListenSpeechToText = this.toggleListenSpeechToText.bind(this);
    this.handleListen = this.handleListen.bind(this);
    this.handleAudioRecording = this.handleAudioRecording.bind(this);
    this.handleAnalyzingsTextForNextScene = this.handleAnalyzingsTextForNextScene.bind(this);
    this.handleButtonNextScene = this.handleButtonNextScene.bind(this);
    this.handleSettingAudioNodesArray = this.handleSettingAudioNodesArray.bind(this);
    this.handleDisplayNextSceneButton = this.handleDisplayNextSceneButton.bind(this);
    this.startAudioSequences = this.startAudioSequences.bind(this);
    this.playAudio = this.playAudio.bind(this);
    this.callBackAudio = this.callBackAudio.bind(this);
    this.state = {
      showSubtitle: false,
      showPrompt: false,
      audioStatus: 'initial',
      isDisplayContentImage: false,
      isDiplayNextSceneButton: false,
      micPermissionStatus: null,
      isReadyToRecord: false,
      listeningText: false,
      mediaStreamObj: null,
      mediaRecorder: null,
      audioFile: null,
      requestNextSceneOrder: null,
      audioArray: [],
      audioIdx: 0,
      audioNode: new Audio(),
      sceneKeyWords: [],
      isContinuePlay: false,
      isDoneRendering: false
    }
    this.constraintObj = {
      audio: true 
    }
    this.stream = '';
    this.wordTexts = React.createRef();
  }

  static getDerivedStateFromProps(props) {
    const { storyContent: { scene } } = props
    if (props.loading.content === false) {
      return {
        sceneKeyWords: scene.scene_keywords,
        isDoneRendering: true
      }
    } else {
      return {
        audioIdx: 0,
        audioStatus: 'initial',
        showSubtitle: false,
        showPrompt: false,
        sceneKeyWords: [],
        audioArray: [],
        isReadyToRecord: false,
        isDiplayNextSceneButton: false,
        isDisplayContentImage: false,
        isDoneRendering: false
      }
    }
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
          mediaStreamObj,
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

  componentDidUpdate(prevProps, prevState){
    const { loading } = this.props;
    const { isContinuePlay, isDoneRendering } = this.state;
    if (prevProps.loading.content !== loading.content) {
      this.handleAudioRecording();
      this.handleSettingAudioNodesArray();
    }

    if ((prevState.isDoneRendering !== isDoneRendering) && isContinuePlay ) {
      this.handleContentAudioStatus();
    }
  }

  componentWillUnmount() {
    this._isMounted = false;
    if (this.stream) {
      this.stream.getTracks()
      .forEach((track) => track.stop());
    }
    this.state.audioNode.pause()
    this.props.removeStoryContents();
    this.props.resetStoryStatus();
  }

  handleSettingAudioNodesArray() {
    const arrPlaceHolder = [];
    const arrayObjSceneSpeakers = this.props.storyContent.scene.story_scene_speakers;
    arrayObjSceneSpeakers.forEach( speakerSceneObj => {
      const audioNode = new Audio();
      audioNode.src = speakerSceneObj.audio_url
      arrPlaceHolder.push(audioNode)
    })

    this.setState({
      audioArray: arrPlaceHolder
    })
  }
  

  //TODO: add try/catch error handling here when loading audio file
  handleContentAudioStatus() {
    if (!this.state.micPermissionStatus) return
    if (this.state.audioStatus === 'playing') {
      this.setState({
        audioStatus: 'paused',
        isReadyToRecord: false
      }, () => {
        this.state.audioNode.pause()
      })
    } else if (this.state.audioStatus === 'paused') {
      this.setState({
        audioStatus: 'playing'
      }, () => {
        this.state.audioNode.play()
      })
    } else if (this.state.audioStatus === 'repeat') {
      this.setState({
        audioStatus: 'playing',
        isReadyToRecord: false,
        audioIdx: 0,
        showPrompt: false
      }, () => {
        this.startAudioSequences()
      })
    } else if (this.state.audioStatus === 'finished') {
      return null
    } else {
      this.setState({
        audioStatus: 'playing',
        isDisplayContentImage: true,
        showPrompt: false
      }, () => {
        this.startAudioSequences()
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
    scene_keywords.forEach((x, idx) => {
      if (textValue.includes(x.keyword)) {
        correctIdx = idx;
        return true
      }
    })

    if ((correctIdx >= 0) && scene_keywords[correctIdx].next_scene_order === order) {
      console.log('repeat the scene')
    } else if (correctIdx >= 0) {
      this.setState({
        requestNextSceneOrder: scene_keywords[correctIdx].next_scene_order,
        isDiplayNextSceneButton: true
      })
      console.log('make an HTTP call')
    } else {
      console.log('no words found matching')
      this.setState({
        requestNextSceneOrder: null,
        isDiplayNextSceneButton: true
      })
    }
  }

  handleButtonNextScene() {
    const { requestNextSceneOrder } = this.state;
    if (!requestNextSceneOrder) return
    const { storyContent, storyStatus } = this.props
    const keywords = storyContent.scene.scene_keywords;
    const lastSpokenSpeakerIndex = storyContent.scene.story_scene_speakers.length - 1;
    if (keywords.length) {
      const textValue = this.wordTexts.current.innerText;
      const data = new FormData();
      data.append('user_story_uid', storyStatus.userStoryID);
      data.append('user_audio', this.state.audioFile);
      data.append('audio_text', textValue);
      data.append('story_scene_speaker_id', storyContent.scene.story_scene_speakers[lastSpokenSpeakerIndex].id);
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

    this.setState({
      isContinuePlay: true
    })
  }

  startAudioSequences() {
    const arr = this.state.audioArray;
    this.playAudio(arr[this.state.audioIdx]);
    
  }

  playAudio(audio){
    if ((!audio || !(audio instanceof Audio))) return;
    this.setState({
      audioNode: audio
    }, () => {
      this.state.audioNode.addEventListener('ended', this.callBackAudio)
      this.state.audioNode.play();
    })
  }

  callBackAudio(event) {
    const arr = this.state.audioArray;
    event.target.removeEventListener('ended', this.callBackAudio)
    if (this.state.audioIdx >= this.props.storyContent.scene.story_scene_speakers.length - 1) {
      this.setState({
        audioStatus: 'finished',
        isReadyToRecord: true,
        showPrompt: true,
      }, () => this.handleDisplayNextSceneButton())
    } else {
      this.setState({
        audioIdx: this.state.audioIdx + 1
      }, () => {
        this.playAudio(arr[this.state.audioIdx]);
      })
    }
    
  }

  handleDisplayNextSceneButton() {
    const { isReadyToRecord } = this.state;
    if (!isReadyToRecord) return
    const { storyContent: { scene } } = this.props;
    const keywords = scene.scene_keywords;
    if (keywords.length <= 0 && scene.type !== 'end') {
      this.setState({
        isDiplayNextSceneButton: true,
        requestNextSceneOrder: scene.next_scene_order
      })
    } else if (scene.type === 'end') {
      this.setState({
        isDiplayNextSceneButton: true,
        requestNextSceneOrder: 'end'
      })
    }
  }

  displayDesktopLayout() {
    const { uid } = this.props;
    const { listeningText, sceneKeyWords, requestNextSceneOrder, isDiplayNextSceneButton } = this.state;
    const isKeyWordsAvailable = sceneKeyWords.length > 0;
    return (
      <div className="page">
        <div className="top-buttons">
          <div>
            <div className="btn btn-dark-blue" onClick={() => this.updateAudioStatus('repeat')}>Repeat Audio</div>
          </div>
          <div>
            <div className={`btn btn-dark-blue ${this.state.showSubtitle ? 'btn-dark-blue-active' : ''}`} onClick={this.handleShowSubtitleDialog}>Hide Subtitles</div>
          </div>
          <div>
            <div className={"btn btn-dark-blue"}>Restart</div>
          </div>
          <div>
            <div className="btn btn-dark-blue">
              <Link to={`/story/${uid}`}>Home</Link>
            </div>
          </div>
        </div>
        <ContentScreen 
          isDisplayContentImage={this.state.isDisplayContentImage}
          showSubtitle={this.state.showSubtitle}
          showPrompt={this.state.showPrompt}
          micPermissionStatus={this.state.micPermissionStatus}
          handleContentAudioStatus={this.handleContentAudioStatus}
          audioIdx={this.state.audioIdx}
          storyContent={this.props.storyContent} 
        />

        <div className="bottom-buttons">
          <div className={`btn ${isKeyWordsAvailable ? '' : 'hide' }`}>
            <button onClick={this.toggleListenSpeechToText} id="btnStartRecord" className={`btn-record ${listeningText ? 'Rec' : 'notRec'}`}>
              Record Button
            </button>
          </div>
          {isDiplayNextSceneButton ? <div onClick={this.handleButtonNextScene} className="btn btn-dark-blue">{requestNextSceneOrder ? 'Next Scene' : 'Try Record Again!'}</div> : null }
        </div>
        <div className="speech-text-container">
          <div id="speech-to-text">
            <FontAwesomeIcon icon={faMicrophone} color="green" />
            <span ref={this.wordTexts} className="word-texts"></span>
          </div>
        </div>
        <audio className="sound-clips">
        </audio>
      </div>
    )
  }

  render() {
    const { loading } = this.props;
    if (loading.content) {
      return (
        <div className="react-spinner-container ">
          <ReactLoading type={'spin'} color={'#51B2F3'} height={40} width={105}  />
        </div>
      )
    }
    return (
      <div id="story-media">
        {this.displayDesktopLayout()}
      </div>
    )
  }
}

const mapStateToProps = ({ authInfo, storiesInfo, storyContent, storyStatus, loading }) => ({
  authInfo,
  storiesInfo,
  storyContent,
  storyStatus,
  loading
})

const mapDispatchToProps = {
  getStoryStarted,
  removeStoryContents,
  resetStoryStatus,
  getAsyncNextScene,
  getStoryContents,
  completeStory
}


export default connect(mapStateToProps, mapDispatchToProps)(StartStoryPage);