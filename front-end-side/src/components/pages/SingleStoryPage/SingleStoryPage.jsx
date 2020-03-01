import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import StripeCheckout from 'react-stripe-checkout';

import { startLoadingContent } from '../../../actions';
import './SingleStoryPage.scss';

class SingleStoryPage extends React.Component {
  constructor(props) {
    super(props);
    this.handleInitiatingStory = this.handleInitiatingStory.bind(this);
    this.handleToken = this.handleToken.bind(this);
    this.state = {
      isStoryStarted: false,
      price: 5, //USD dollar,
      BASE_URL: 'http://127.0.0.1:5000'
    }
  }

  handleInitiatingStory(event) {
    event.preventDefault();
    const { uid, routeProps: { history } } = this.props;
    this.props.startLoadingContent()
    history.push(`/story/${uid}/start`)
  }

  async handleToken(token) {
    const { authInfo: { serverResponse: { user }} } = this.props;
    const STRIPE_ENDPOINT = `${this.state.BASE_URL}/subscriptions`;
    let headers = new Headers();
    const jwtToken = localStorage.getItem('access_token')
    headers.set('x-access-token', jwtToken);
    headers.set('Accept', 'application/json');
    headers.set('Content-Type', 'application/json; charset=UTF-8');

    const obj = {
      user_uid: user.uid,
      payment_token: token.id
    }

    const parameters = {
      method: 'POST',
      headers,
      body: JSON.stringify(obj)
    }

    const response = await fetch(STRIPE_ENDPOINT, parameters);
    const json = await response.json();
    console.log(json, 'this is json response')

  }

  render() {
    const { name, image_url, description, difficulty, length, genre, is_demo, is_visible } = this.props;
    return (
      <div id="story" className="page">
        <div className="story-info-container">
          <div className="content-container">
            <h2>{name}</h2>
            <hr />
            <div className="content-description">
              <div>{description}</div>
              <br />
              <div>Difficulty Level: {difficulty}</div>
              <br />
              <div>Length Time: {length}</div>
              <br />
              <div>Genre: {genre}</div>
            </div>
            <br />
          </div>

          <div className="interaction-container">
            <div>
              <img className='story-cover' src={image_url} alt="story-cover" />
            </div>
            <div className="buttons-container">
              {is_visible ? 
                <button onClick={this.handleInitiatingStory} className="btn btn-green">
                  Start
                </button>
                :
                <StripeCheckout 
                  token={this.handleToken}
                  stripeKey="pk_test_mJHbhp4HBDDMBpIfhhzZ9THz00JcFeKvRA"
                  amount={this.state.price * 100}
                  name={name}
                  description="this is description"
                  >
                    <button className="btn btn-green">
                      Subscribe To Play
                    </button>
                </StripeCheckout>

              }

                <Link className="cancel" to="/app"> 
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 2L2 22" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 2L22 22" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                </Link>

            </div>
          </div>

        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ authInfo }) => ({
  authInfo
})

const mapDispatchToProps = {
  startLoadingContent
}

export default connect(mapStateToProps, mapDispatchToProps)(SingleStoryPage);