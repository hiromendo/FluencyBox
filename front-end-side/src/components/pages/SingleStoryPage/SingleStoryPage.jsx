import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { getStoryStarted } from '../../../actions';
import './SingleStoryPage.scss';

class SingleStoryPage extends React.Component {
  constructor(props) {
    super(props);
    this.handleInitiatingStory = this.handleInitiatingStory.bind(this);
    this.state = {
      isStoryStarted: false
    }
  }

  handleInitiatingStory(event) {
    event.preventDefault();
    const { authInfo: { serverResponse: { user }}, uid, routeProps: { history } } = this.props;
    const payloadObj = {
      user_uid: user.uid,
      history,
      story_uid: uid
    }

    this.props.getStoryStarted(payloadObj)
  }

  render() {
    const { name, image_url, description, difficulty, length, genre, uid } = this.props
    return (
      <div id="story" className="page">
        <div className="story-info-container">
          <div className="kenzo">
            <div>
              <h2>{name}</h2>
              <div>{description}</div>
              <div>Difficulty Level: {difficulty}</div>
              <div>Length Time: {length}</div>
              <div>Genre: {genre}</div>
              <br />
            </div>
            <div>
              <img className='story-cover' src={image_url} alt="story-cover" />
            </div>
          </div>

          <div className="buttons-container">
            <button onClick={this.handleInitiatingStory} className="btn btn-blue">
              Start
            </button>
            <Link className="cancel" to="/app">Cancel</Link>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  authInfo
})

const mapDispatchToProps = {
  getStoryStarted
}

export default connect(mapStateToProps, mapDispatchToProps)(SingleStoryPage);