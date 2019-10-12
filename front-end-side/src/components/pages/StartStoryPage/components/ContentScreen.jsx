import React from 'react';

const ContentScreen = props => {
    let imgTag;
    let subTitleText;
    const { isDisplayContentImage, showSubtitle } = props
    if (props.storyContent.scene) {
      imgTag = props.storyContent.scene.story_scene_speakers[0].image_url;
      subTitleText = props.storyContent.scene.story_scene_speakers[0].audio_text;
    }

    return (
      <div id="story-content" onClick={props.handleAudioStatus}>
        {showSubtitle ? <div className="subtitle-caption">{subTitleText}</div> : null }
        {isDisplayContentImage ? <img src={imgTag} alt="content screen" /> : <div>Click here to start</div>}
      </div>
    )
}


export default ContentScreen