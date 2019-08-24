import React from 'react';

import './alertMessage.scss'

export const AlertMessage = ({typeAlert, message }) => {
  return (
    <div className={`alert alert-${typeAlert}`} >
      <strong>{message}</strong>
    </div>
  )
}
