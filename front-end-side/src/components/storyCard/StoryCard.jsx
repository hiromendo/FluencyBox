import React from 'react';
import { Col } from 'react-flexbox-grid';

export const StoryCard = ( {infoObj }) => {
  console.log(infoObj)
  console.log('ffiiiiii')
  return (
    <Col xs={12} md={4} lg={4} key={infoObj.uid}>
      <div data-uid={infoObj.uid} className="story-card">
        <img src="http://placekitten.com/400/400" alt={infoObj.description} />
        {/* <img src={infoObj.image_filename} alt={infoObj.description} /> */}
        <div>{infoObj.name}</div>
      </div>
    </Col>
  )
}