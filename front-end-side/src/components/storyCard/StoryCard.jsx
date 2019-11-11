import React from 'react';
import { Link } from 'react-router-dom';

import './StoryCard.scss'

export const StoryCard = ({ infoObj }) => {
  return (
    <div data-uid={infoObj.uid} className="story-card">
      <Link to={`/story/${infoObj.uid}`}>
        <img src={infoObj.image_url} alt={infoObj.description} />
      </Link>
      <div className="story-title">{infoObj.name}</div>
    </div>
  )
}