import React from 'react';

import withMediaData from '../hoc/withMediaData'

class ContentScreen extends React.Component {
  constructor(props) {
    super(props);
    this.handleStartAudio = this.handleStartAudio.bind(this);
    this.state = {
      isStart: false
    }
  }

  handleStartAudio() {
    if (this.state.isStart) return
    this.setState({
      isStart: true
    }, () => {
      this.props.dispatchActionsContainer.audioPlay()
    })
  }

  render() {
    let imgTag;
    if (this.props.mediaData.scene) {
      imgTag = this.props.mediaData.scene.story_scene_speakers[0].image_url;
    }

    return (
      <div id="story-content" onClick={this.handleStartAudio}>
        {this.state.isStart ? <img src={imgTag} alt="content screen" /> : <div>Click here to start</div>}
      </div>
    )
  }
}


export default withMediaData(ContentScreen)