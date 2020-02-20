import React from 'react';
import { connect } from 'react-redux';

import { StoryCard } from '../storyCard/StoryCard';
import './appLayOut.scss';

class AppLayOut extends React.Component {
  constructor(props) {
    super(props);
    this.renderAllStories = this.renderAllStories.bind(this);
  }

  renderAllStories() {
    const { storiesInfo: { story } }  = this.props;
    const listStoryCards = story.map( info => {
      return <StoryCard infoObj={info} key={info.uid} />
    })
    return listStoryCards;
  }

  render() {
    const stories = this.renderAllStories()
    return (
      <div className="dashboard page">
        {stories}
      </div>
    )
  }
}

const mapStateToProps = ({ authInfo, storiesInfo }) => ({
  userInfo: authInfo.serverResponse.user,
  storiesInfo
})


export default connect(mapStateToProps)(AppLayOut);