import React from 'react';

const ContentScreen = props => {
    let imgTag;
    let subTitleText;
    let promptText;
    const { isDisplayContentImage, showSubtitle, micPermissionStatus, audioIdx, showPrompt } = props;
    if (props.storyContent.scene) {
      imgTag = props.storyContent.scene.story_scene_speakers[audioIdx].image_url;
      subTitleText = props.storyContent.scene.story_scene_speakers[audioIdx].audio_text;
      promptText = props.storyContent.scene.story_scene_speakers[audioIdx].prompt;
    }

    if (micPermissionStatus === false ) {
      return (
        <div id="story-content" >
          <div>Display a Popup asking user to permit Microphone usage</div>
      </div>
      )
    }

    return (
      <div id="story-content" onClick={props.handleContentAudioStatus}>
        {showSubtitle ? <div className="subtitle-caption">{subTitleText}</div> : null }
        {isDisplayContentImage ? <img src={imgTag} alt="content screen" /> : <div>Click here to start</div>}
        {showPrompt ? <div className="prompt-caption">{promptText}</div> : null }
      </div>
    )
}


export default ContentScreen