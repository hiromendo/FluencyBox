import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';

import './SingleStoryPage.scss';

class SingleStoryPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isStoryStarted: false
    }
  }

  render() {
    const { name, image_filename, description, difficulty, length, genre } = this.props
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
              <img className='story-cover' src={image_filename} alt="story-cover" />
            </Col>
            
          </Row>
          <Row middle="xs" center="xs" start="md">
            <Col xs={6} md={2} mdOffset={4} lg={2}>
              <button className="btn">Start</button>
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

export default SingleStoryPage;