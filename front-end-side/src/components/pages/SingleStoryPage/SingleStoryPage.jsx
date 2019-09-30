import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';

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
    const { authInfo: { serverResponse: { user }}, uid, routeProps:  {history } } = this.props;
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
        <Grid className="content-container">
          <Row middle="lg" center="xs" start="md" top="md">
            <Col xs={12} md={4} mdOffset={1} lg={4} lgOffset={1}>
              <h2>{name}</h2>
              <div>{description}</div>
              <div>Difficulty Level: {difficulty}</div>
              <div>Length Time: {length}</div>
              <div>Genre: {genre}</div>
              <br />
            </Col>
            <Col xs={12} md={4} mdOffset={2} lg={4} lgOffset={2}>
              <img className='story-cover' src={image_url} alt="story-cover" />
            </Col>
            
          </Row>
          <Row middle="xs" center="xs" start="md">
            <Col xs={6} md={2} mdOffset={5} lg={2}>
              <button onClick={this.handleInitiatingStory} className="btn btn-blue">
                {/* <Link to={`/story/${uid}/start`}>Start</Link> */}
                Start
              </button>
            </Col>
            <Col xs={6} md={2} lg={2}>
              <Link className="cancel" to="/app">Cancel</Link>
            </Col>
          </Row>
        </Grid>
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