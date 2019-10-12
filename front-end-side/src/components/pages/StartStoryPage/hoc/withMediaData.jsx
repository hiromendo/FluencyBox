import React from 'react';
import { connect } from 'react-redux';

import { audioPlay, pauseAudio } from '../../../../actions';

const withMediaData = WrappedComponent => {
  class NewComponent extends React.Component {
    render() {
      const { audioPlay, pauseAudio } = this.props;
      const dispatchActionsContainer = {
        audioPlay,
        pauseAudio
      }
      return (
        <WrappedComponent
          mediaData={this.props.storyContent} 
          dispatchActionsContainer={dispatchActionsContainer} 
        />
      )
    }
  }

  const mapStateToProps = ({ storyContent }) => ({
    storyContent
  })

  const mapDispatchToProps = {
    audioPlay,
    pauseAudio
  }

  return connect(mapStateToProps, mapDispatchToProps)(NewComponent)
}



export default withMediaData;