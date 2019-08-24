import React from 'react'
import Enzyme, { shallow } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import { Login } from './login';

Enzyme.configure({ adapter: new Adapter() })

function setup() {
  const props = {
    loading: jest.fn(),
    getLogin: jest.fn(),
    history: jest.fn()
  }

  const enzymeWrapper = shallow(<Login {...props} />)

  return {
    props,
    enzymeWrapper
  }
}
describe('components', () => {
  describe('Header', () => {
    it('should render self and subcomponents', () => {
      const { enzymeWrapper } = setup()
      expect(enzymeWrapper.find('form').hasClass('form')).toBe(true)

      // expect(enzymeWrapper.find('h1').text()).toBe('todos')

      // const todoInputProps = enzymeWrapper.find('TodoTextInput').props()
      // expect(todoInputProps.newTodo).toBe(true)
      // expect(todoInputProps.placeholder).toEqual('What needs to be done?')
    })

    it('renders three <Login /> components', () => {
      const wrapper = shallow(<Login />);
      // expect(wrapper.find('input')).to.have.lengthOf(3);
      console.log(wrapper.debug())
    });
  })
})