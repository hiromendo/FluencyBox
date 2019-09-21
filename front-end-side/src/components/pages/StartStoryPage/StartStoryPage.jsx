import React from 'react';
import { Grid, Row, Col } from 'react-flexbox-grid';

import './StartStoryPage.scss';

class StartStoryPage extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      page: false
    }
  }

  render() {
    return (
      <div id="story-start">
        <Grid className="content-container">
          <Row middle="xs">
            <Col xs={4} xsOffset={1}>
              <div>Repeat Audio</div>
            </Col>
            <Col xs={4} xsOffset={2}>
              <div>Hide Subtitles</div>
            </Col>
          </Row>
          <Row center="xs">
            <Col xs={12}>
              <div style={{border: '1px solid red'}}>Content Here</div>
            </Col>
          </Row>
          <Row>
            <Col xs={2} xsOffset={1}>
              Restart
            </Col>
            <Col xs={4} xsOffset={1}>
              Record Button
            </Col>
            <Col xs={2} xsOffset={1}>
              Home
            </Col>
          </Row>
        </Grid>
      </div>
    )
  }
}

export default StartStoryPage;