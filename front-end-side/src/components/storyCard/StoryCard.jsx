import React from 'react';
import { Col } from 'react-flexbox-grid';
import { Link } from 'react-router-dom';

import './StoryCard.scss'

export const StoryCard = ({ infoObj }) => {

  return (
    <Col xs={12} md={4} lg={4} key={infoObj.uid}>
      <div data-uid={infoObj.uid} className="story-card">
        <Link to={`/story/${infoObj.uid}`}>
          <img src={infoObj.image_filename} alt={infoObj.description} />
          {/* <img src="http://placekitten.com/400/400" alt={infoObj.description} /> */}
        </Link>
        <div className="story-title">{infoObj.name}</div>
      </div>
    </Col>
  )
}