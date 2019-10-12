import React from 'react';

const ContentScreen = props => {
    let imgTag;
    const { isDisplayContentImage } = props
    if (props.storyContent.scene) {
      imgTag = props.storyContent.scene.story_scene_speakers[0].image_url;
    }

    return (
      <div id="story-content" onClick={props.handleAudioStatus}>
        {isDisplayContentImage ? <img src={imgTag} alt="content screen" /> : <div>Click here to start</div>}
      </div>
    )
}


export default ContentScreen