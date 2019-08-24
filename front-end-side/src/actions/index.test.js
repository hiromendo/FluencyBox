import * as actions from './index';


describe('testing actions', () => {
  it('should create an action to start loading', () => {
    const expectedAction = {
      type: actions.START_LOADING,
    }
    expect(actions.startLoading()).toEqual(expectedAction)
  })

  it('should create an action to stop loading', () => {
    const expectedAction = {
      type: actions.END_LOADING,
    }
    expect(actions.endLoading()).toEqual(expectedAction)
  })

  it('should create an action to get current user info', () => {
    const userInfo = {};
    const expectedAction = {
      type: actions.GET_CURRENT_USER,
      userInfo
    }
    expect(actions.getCurrentUser(userInfo)).toEqual(expectedAction)
  })

  it('should create an action to call getLogin', () => {
    const userInfo = {};
    const history = {};
    const expectedAction = {
      type: actions.GET_LOGIN,
      userInfo,
      history
    }
    expect(actions.getLogin(userInfo, history)).toEqual(expectedAction)
  })

  it('should create an action to call sendRegister', () => {
    const userInfo = {};
    const history = {};
    const expectedAction = {
      type: actions.SEND_REGISTER,
      userInfo,
      history
    }
    expect(actions.sendRegister(userInfo, history)).toEqual(expectedAction)
  })


  it('should create an action to call setCurrentUser', () => {
    const data = {};
    const expectedAction = {
      type: actions.SET_CURRENT_USER,
      data
    }
    expect(actions.setCurrentUser(data)).toEqual(expectedAction)
  })

  it('should create an action to call removeCurrentUser', () => {
    const expectedAction = {
      type: actions.REMOVE_CURRENT_USER,
    }
    expect(actions.removeCurrentUser()).toEqual(expectedAction)
  })

})