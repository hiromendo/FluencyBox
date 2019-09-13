import React from 'react';
import { connect } from 'react-redux';
import { Grid, Row, Col } from 'react-flexbox-grid';

import { StoryCard } from '../storyCard/StoryCard';
import './appLayOut.scss';
import { isNoop } from '@babel/types';

class AppLayOut extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mockStories: []
    }
    this.renderAllStories = this.renderAllStories.bind(this);
  }

  componentDidMount() {
    this.setState({
      mockStories: [ {
        "description": "this a story where you interview two people", 
        "difficulty": "hard",
        "genre": "professional",
        "image_filename": "interviewcover.jpg",
        "is_demo": true,
        "length": "10 minutes",
        "name": "interview",
        "uid": "e534fefd-3e25-430e-87ec-45403794a883"
        }]
    })
  }

  renderAllStories() {
    const { storiesInfo: { story } }  = this.props;
    const listItems = story.map( info => {
      console.log(info, 'this is info')
      return <StoryCard infoObj={info} key={info.uid} />
    })
    return listItems;
  }

  render() {
    const stories = this.renderAllStories()
    return (
      <main>
        <Grid>
          <Row middle="lg">
            {stories}
          </Row>
        </Grid>
      </main>
    )
  }
}

const mapStateToProps = ({ authInfo, storiesInfo }) => ({
  userInfo: authInfo.serverResponse.user,
  storiesInfo
})


export default connect(mapStateToProps)(AppLayOut);