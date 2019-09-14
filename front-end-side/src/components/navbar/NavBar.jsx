import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';
import { elastic as Menu } from 'react-burger-menu';

import './NavBar.scss';

const preventDefault = e => {
  e.preventDefault()
}

export const NavBar = props => {
  const isMenuOpen = state => {
    const { isOpen } = state;
    const bodyTag = document.querySelector('body');
    if (isOpen) {
      bodyTag.addEventListener('touchmove',  preventDefault, { passive: false })
    } else {
      bodyTag.removeEventListener('touchmove', preventDefault, { passive: false })
    }
  };


  return (
    <nav id="top-nav">
      <ul id="desktop-nav">
        <Grid>
          <Row middle="md">
            <Col xs={6} md={3} lg={3} >
              <li>
                <h1 className="brand-text">
                  <Link to="/app">FluencyBox</Link></h1>
              </li>
            </Col>
            <Col xs={6} md={2} mdOffset={1} lg={1} lgOffset={5}>
              <li>
                <Link to="/app">Dashboard</Link>
              </li> 
            </Col>
            <Col xs={6} md={2} lg={1}>
              <li>
                <Link to="/userprofile">UserProfile</Link>
              </li> 
            </Col>
            <Col xs={6} md={2} lg={1}>
              <li>
                <Link to="/aboutus">About Us</Link>
              </li> 
            </Col>
            <Col xs={6} md={2} lg={1}>
              <li>
                <a href="#" onClick={props.logOffUser}>Logout</a>
              </li> 
            </Col>
          </Row>
        </Grid>
      </ul>
      <div id="mobile-nav">
        <h1 className="brand-text"><Link to="/app">FluencyBox</Link></h1>
        <Menu width={220} onStateChange={ isMenuOpen }>
          <Link to="/app">Dashboard</Link>
          <Link to="/userprofile">UserProfile</Link>
          <Link to="/aboutus">About Us</Link>
          <a href="#" onClick={props.logOffUser}>Logout</a>
        </Menu>
      </div>
    </nav>
  )
}