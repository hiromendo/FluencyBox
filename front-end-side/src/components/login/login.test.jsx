import React from 'react'
import Enzyme, { shallow } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import renderer from 'react-test-renderer';
import { BrowserRouter } from 'react-router-dom'; 

import { Login } from './login';

Enzyme.configure({ adapter: new Adapter() })

describe('Login component', () => {
  it('should match snapshot', () => {
    const component = renderer.create(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    let tree = component.toJSON();
    expect(tree).toMatchSnapshot();
  })
})