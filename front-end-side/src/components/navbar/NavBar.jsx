import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Row, Col } from 'react-flexbox-grid';
import { elastic as Menu } from 'react-burger-menu';

import './NavBar.scss';

const preventDefault = e => {
  e.preventDefault()
}

// export const NavBar = props => {

//   const beforeSigningOff = () => {
//     const bodyTag = document.querySelector('body');
//     const overLayBg = document.querySelector('.bm-overlay');
//     const overLayWrap = document.querySelector('.bm-menu-wrap');
  
//     setTimeout(() => {
//       /* workaround to have smooth animation transition */
//       overLayBg.classList.remove('bm-overlay-expand');
//       overLayWrap.classList.remove('bm-overlay-expand');
//     }, 0)
//     bodyTag.removeEventListener('touchmove', preventDefault, { passive: false })

//     props.logOffUser()
//   }

//   const isMenuOpen = state => {
//     const { isOpen } = state;
//     const bodyTag = document.querySelector('body');
//     const overLayBg = document.querySelector('.bm-overlay');
//     const overLayWrap = document.querySelector('.bm-menu-wrap');
//     if (isOpen) {
//       bodyTag.addEventListener('touchmove',  preventDefault, { passive: false })
//       overLayBg.classList.add('bm-overlay-expand');
//       overLayWrap.classList.add('bm-overlay-expand');
//     } else {
//       setTimeout(() => {
//         /* workaround to have smooth animation transition */
//         overLayBg.classList.remove('bm-overlay-expand');
//         overLayWrap.classList.remove('bm-overlay-expand');
//       }, 0)
//       bodyTag.removeEventListener('touchmove', preventDefault, { passive: false })
//     }
//   };

//   return (
//     <nav id="top-nav">
//       <ul id="desktop-nav">
//         <Grid>
//           <Row middle="md">
//             <Col xs={6} md={3} lg={3} >
//               <li>
//                 <Link to="/app"><img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" /></Link>
                
//               </li>
//             </Col>
//             <Col xs={6} md={2} mdOffset={1} lg={1} lgOffset={5}>
//               <li>
//                 <Link to="/app">Dashboard</Link>
//               </li> 
//             </Col>
//             <Col xs={6} md={2} lg={1}>
//               <li>
//                 <Link to="/userprofile">UserProfile</Link>
//               </li> 
//             </Col>
//             <Col xs={6} md={2} lg={1}>
//               <li>
//                 <Link to="/aboutus">About Us</Link>
//               </li> 
//             </Col>
//             <Col xs={6} md={2} lg={1}>
//               <li>
//                 <a href="#" onClick={() => beforeSigningOff()}>Logout</a>
//               </li> 
//             </Col>
//           </Row>
//         </Grid>
//       </ul>
//       <div id="mobile-nav">
//         <Link to="/app"><img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" /></Link>
        
//         <Menu width={220} onStateChange={ isMenuOpen }>
//           <Link to="/app">Dashboard</Link>
//           <Link to="/userprofile">UserProfile</Link>
//           <Link to="/aboutus">About Us</Link>
//           <a href="#" onClick={() => beforeSigningOff()}>Logout</a>
//         </Menu>
//       </div>
//     </nav>
//   )
// }


class NavBar extends React.Component {
  constructor(props) {
    super(props);
    this.handleStateChange = this.handleStateChange.bind(this);
    this.beforeSigningOff = this.beforeSigningOff.bind(this);
    this.isMenuOpen = this.isMenuOpen.bind(this);
    this.state = {
      menuOpen: false
    }
  }

  handleStateChange(state) {
    this.setState({menuOpen: state.isOpen}) 
  }

  closeMenu () {
    this.setState({menuOpen: false})
  }

  beforeSigningOff() {
    const bodyTag = document.querySelector('body');
    const overLayBg = document.querySelector('.bm-overlay');
    const overLayWrap = document.querySelector('.bm-menu-wrap');
  
    setTimeout(() => {
      /* workaround to have smooth animation transition */
      overLayBg.classList.remove('bm-overlay-expand');
      overLayWrap.classList.remove('bm-overlay-expand');
    }, 0)
    bodyTag.removeEventListener('touchmove', preventDefault, { passive: false })

    this.props.logOffUser()
  }

  isMenuOpen(hamburgerMenuState) {
    const { isOpen } = hamburgerMenuState;
    this.setState({ menuOpen: isOpen }) ;

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
  }

  render() {
    return (
      <nav id="top-nav">
        <ul id="desktop-nav">
          <Grid>
            <Row middle="md">
              <Col xs={6} md={3} lg={3} >
                <li>
                  <Link to="/app"><img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" /></Link>
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
                  <a href="#" onClick={() => this.beforeSigningOff()}>Logout</a>
                </li> 
              </Col>
            </Row>
          </Grid>
        </ul>
        <div id="mobile-nav">
          <div className="logo-container">
            <Link to="/app" onClick={() => this.closeMenu()}>
              <img className="logo-brand" src="https://uploads-ssl.webflow.com/5d40e2a7625e7f495119ba08/5d78bd2c584e14d8417c6306_hanasulogo2.png" alt="logo" />
            </Link>
          </div>
          
          <Menu width={220} isOpen={this.state.menuOpen} onStateChange={(state) => this.isMenuOpen(state)}>
            <Link onClick={() => this.closeMenu()} to="/app">Dashboard</Link>
            <Link onClick={() => this.closeMenu()} to="/userprofile">UserProfile</Link>
            <Link onClick={() => this.closeMenu()} to="/aboutus">About Us</Link>
            <a href="#" onClick={() => this.beforeSigningOff()}>Logout</a>
          </Menu>
        </div>
      </nav>
    )
  }
}

export default NavBar;