import React from 'react';
import { connect } from 'react-redux';

const withMediaData = WrappedComponent => {
  class NewComponent extends React.Component {
    render() {
      return <WrappedComponent mediaData={this.props.storyContent} />
    }
  }

  const mapStateToProps = ({ storyContent }) => ({
    storyContent
  })

  return connect(mapStateToProps)(NewComponent)
}

export default withMediaData;