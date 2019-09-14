import React from 'react';
import { connect } from 'react-redux';
import { Grid, Row } from 'react-flexbox-grid';

import { StoryCard } from '../storyCard/StoryCard';
import './appLayOut.scss';

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
        "image_filename": "http://placekitten.com/400/400",
        "is_demo": true,
        "length": "10 minutes",
        "name": "interview",
        "uid": "e534sdf3"
      },{
        "description": "this a story where you interview two people", 
        "difficulty": "hard",
        "genre": "professional",
        "image_filename": "http://placekitten.com/400/400",
        "is_demo": true,
        "length": "10 minutes",
        "name": "interview",
        "uid": "e534fefd-3e25-430e-87esdf83"
        
      },{
        "description": "this a story where you interview two people", 
        "difficulty": "hard",
        "genre": "professional",
        "image_filename": "http://placekitten.com/400/400",
        "is_demo": true,
        "length": "10 minutes",
        "name": "interview",
        "uid": "e534fefd-3e25-430e-87ec-45403794ds"
        }
      ]
    })
  }

  renderAllStories() {
    const { storiesInfo: { story } }  = this.props;
    const { mockStories }  = this.state;
    const listItems = mockStories.map( info => {
      return <StoryCard infoObj={info} key={info.uid} />
    })
    return listItems;
  }

  render() {
    const stories = this.renderAllStories()
    return (
      <main id="main-content">
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