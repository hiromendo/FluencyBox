import React from 'react';
import { NavLink } from 'react-router-dom';
import { slide as Menu } from 'react-burger-menu';

import './NavBar.scss';

const preventDefault = e => {
  e.preventDefault()
}

class NavBar extends React.Component {
  constructor(props) {
    super(props);
    this.closeMenu = this.closeMenu.bind(this);
    this.beforeSigningOff = this.beforeSigningOff.bind(this);
    this.handleAddingTouchEventListener = this.handleAddingTouchEventListener.bind(this);
    this.handleRemoveTouchEventListener = this.handleRemoveTouchEventListener.bind(this);
    this.handleStateChange = this.handleStateChange.bind(this);
    this.state = {
      menuOpen: false
    }
  }

  closeMenu () {
    this.setState({ menuOpen: false });
  }

  beforeSigningOff() {
    // const bodyTag = document.querySelector('body');
    // const overLayBg = document.querySelector('.bm-overlay');
    // const overLayWrap = document.querySelector('.bm-menu-wrap');
  
    // /* workaround to have smooth animation transition */
    // setTimeout(() => {
    //   overLayBg.classList.remove('bm-overlay-expand');
    //   overLayWrap.classList.remove('bm-overlay-expand');
    // }, 0)
    // bodyTag.removeEventListener('touchmove', preventDefault, { passive: false })

    this.props.logOffUser();
  }

  handleAddingTouchEventListener() {
    const bodyTag = document.querySelector('body');
    const overLayBg = document.querySelector('.bm-overlay');
    const overLayWrap = document.querySelector('.bm-menu-wrap');

    bodyTag.addEventListener('touchmove',  preventDefault, { passive: false })
    overLayBg.classList.add('bm-overlay-expand');
    overLayWrap.classList.add('bm-overlay-expand');

  }

  handleRemoveTouchEventListener() {
    const bodyTag = document.querySelector('body');
    const overLayBg = document.querySelector('.bm-overlay');
    const overLayWrap = document.querySelector('.bm-menu-wrap');

    setTimeout(() => {
      /* workaround to have smooth animation transition */
      overLayBg.classList.remove('bm-overlay-expand');
      overLayWrap.classList.remove('bm-overlay-expand');
    }, 0)
    bodyTag.removeEventListener('touchmove', preventDefault, { passive: false });
  }

  handleStateChange(hamburgerMenuState) {
    const { isOpen } = hamburgerMenuState;
    this.setState({ menuOpen: isOpen }) ;
    if (isOpen) {
      this.handleAddingTouchEventListener()
    } else {
      this.handleRemoveTouchEventListener()
    }
  }

  renderNavList() {
    const isLoggedIn = localStorage.access_token;
    if (isLoggedIn) {
      return (
        <ul id="desktop-nav">
          <li className="logo-brand-container">
            <NavLink to="/app"><img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" />
            </NavLink>
          </li>
          <li>
            <NavLink to="/app">Home</NavLink>
          </li>
          <li>
            <NavLink to="/reports">Reports</NavLink>
          </li>
          <li>
            <NavLink to="/userprofile">UserProfile</NavLink>
          </li>
          <li>
            <NavLink to ="/about">About</NavLink>
          </li>
          <li>
            <NavLink onClick={() => this.beforeSigningOff()} to="/login">Logout</NavLink> 
          </li>
        </ul>
      )
    } else {
      return (
        <ul id="desktop-nav">
          <li className="logo-brand-container">
            <NavLink to="/app"><img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" />
            </NavLink>
          </li>
          <li>
            <NavLink to ="/about">About</NavLink>
          </li>
        </ul>
      )
    }
  }

  render() {
    const kenzo = window.location.pathname === "/login" || window.location.pathname ==='/resetpassword';

    return (
      <nav id="top-nav">
        {this.renderNavList()}
        <div id="mobile-nav">
          {/* <div className="logo-container">
            <NavLink to="/app" onClick={this.closeMenu}>
              <img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" />
            </NavLink>
          </div>
          
          <Menu width={220} isOpen={this.state.menuOpen} onStateChange={(state) => this.handleStateChange(state)}>
            <NavLink onClick={this.closeMenu} to="/app">Dashboard</NavLink>
            <NavLink onClick={this.closeMenu} to="/userprofile">UserProfile</NavLink>
            <NavLink onClick={this.closeMenu} to="/aboutus">About Us</NavLink>
            <NavLink onClick={() => this.beforeSigningOff()} to="/login">Logout</NavLink>
          </Menu> */}
        </div>
      </nav>
    )
  }
}

export default NavBar;