import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';
import { connect } from 'react-redux';
import throttle from 'lodash.throttle';

import { getStoryStarted, removeStoryContents } from '../../../actions';

import ContentScreen from './components/ContentScreen'
import './StartStoryPage.scss';

class StartStoryPage extends React.Component {
  constructor(props) {
    super(props);
    this.displayDesktopLayout = this.displayDesktopLayout.bind(this);
    this.displayMobileLayOut = this.displayMobileLayOut.bind(this);
    this.handleShowSubtitleDialog = this.handleShowSubtitleDialog.bind(this);
    this.state = {
      isMobile: false,
      showSubtitle: false
    }
    this.audioNode = new Audio();
  }

  componentDidMount() {
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
  }
  
  /* props recieve from redux to indicate audio play */
  componentDidUpdate() {
    console.log(this.props.storyContent.scene.story_scene_speakers[0].audio_url, '<===')
    this.audioNode.src = this.props.storyContent.scene.story_scene_speakers[0].audio_url;
    this.audioNode.play()
  }
  
  componentWillUnmount() {
    console.log('pause')
    this.audioNode.pause()
    this.props.removeStoryContents();
  }
  
  throttledHandleWindowResize = () => {
    //TODO: add a throttle here for optimzation purpose
    this.setState({ isMobile: window.innerWidth < 768 })
  }

  handleShowSubtitleDialog() {
    this.setState({
      showSubtitle: !this.state.showSubtitle
    }, () => {
      console.log(this.state.showSubtitle)
    })
  }

  displayDesktopLayout() {
    const { uid } = this.props
    return (
      <Grid>
        <Row middle="md">
          <Col md={3} mdOffset={1}>
            <div className="btn btn-dark-blue">Repeat Audio</div>
          </Col>
          <Col md={4} mdOffset={1}>
            <div className="btn btn-dark-blue" onClick={this.handleShowSubtitleDialog}>Hide Subtitles</div>
          </Col>
          <Col md={1}>
            <div className="btn btn-dark-blue">Restart</div>
          </Col>
          <Col md={1}>
            <div className="btn btn-dark-blue">
              <Link to={`/story/${uid}`}>Home</Link>
            </div>
          </Col>
        </Row>
        <Row center="md">
          <Col md={12}>
            <ContentScreen />
          </Col>
        </Row>
        <Row>
          <Col md={3} mdOffset={1}>
          <div className="btn btn-dark-blue">
            Record Again
          </div>
          </Col>
          <Col md={2} mdOffset={1}>
            <div className="btn btn-dark-blue">
              Record Button
            </div>
          </Col>
          <Col md={3} mdOffset={2}>
            <div className="btn btn-dark-blue">
              Next Scene
            </div>
          </Col>
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
  removeStoryContents
}


export default connect(mapStateToProps, mapDispatchToProps)(StartStoryPage);