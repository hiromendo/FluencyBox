import React from 'react';
import { connect } from 'react-redux';

import { audioPlay } from '../../../../actions';

const withMediaData = WrappedComponent => {
  class NewComponent extends React.Component {
    render() {
      const { audioPlay } = this.props;
      const dispatchActionsContainer = {
        audioPlay
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
    audioPlay
  }

  return connect(mapStateToProps, mapDispatchToProps)(NewComponent)
}



export default withMediaData;