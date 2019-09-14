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
    console.log('never sdfsdakl')
    const { isOpen } = state;
    const bodyTag = document.querySelector('body');
    const overLayBg = document.querySelector('.bm-overlay');
    const overLayWrap = document.querySelector('.bm-menu-wrap');
    if (isOpen) {
      bodyTag.addEventListener('touchmove',  preventDefault, { passive: false })
      overLayBg.classList.add('bm-overlay-expand');
      overLayWrap.classList.add('bm-overlay-expand');
    } else {
      setTimeout(() => {
        /* workaround to have smooth animation transition */
        overLayBg.classList.remove('bm-overlay-expand');
        overLayWrap.classList.remove('bm-overlay-expand');
      }, 0)
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