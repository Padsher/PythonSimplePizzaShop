import requests
from assertpy import assert_that
from serverParams import url
from common import clearDatabase, registerUser
from repository.DatabaseClient import databaseClient

def test_register():
    clearDatabase()
    resp = requests.post(
        f'{url}/register',
        json = { 'login': 'test', 'password': 'my_pass'}
    )

    accessToken = resp.json()['access']
    resp = requests.get(
        f'{url}/whoami',
        headers = { 'authorization': f'Bearer {accessToken}' }
    )
    body = resp.json()
    assert body['login'] == 'test'
    assert isinstance(body['id'], int)

def test_login():
    clearDatabase()
    userId = registerUser('loginTest', 'login_pass')

    resp = requests.post(
        f'{url}/login',
        json = { 'login': 'loginTest', 'password': 'login_pass' }
    )
    accessToken = resp.json()['access']
    resp = requests.get(
        f'{url}/whoami',
        headers = { 'authorization': f'Bearer {accessToken}' }
    ).json()
    assert_that(resp).is_equal_to({ 'id': userId, 'login': 'loginTest' })

    # test invalid password
    respInvalid = requests.post(
        f'{url}/login',
        json = { 'login': 'loginTest', 'password': 'invalid_pass' }
    )
    assert respInvalid.status_code == 400
    assert_that(respInvalid.json()).is_equal_to({ 'error': 'Invalid credentials' })

def test_refresh():
    clearDatabase()
    userId = registerUser('loginTest', 'login_pass')
    resp = requests.post(
        f'{url}/login',
        json = { 'login': 'loginTest', 'password': 'login_pass' }
    ).json()
    accessToken, refreshToken = resp['access'], resp['refresh']

    resp = requests.post(
        f'{url}/refresh',
        headers = { 'authorization': f'Bearer {refreshToken}' }
    ).json()

    newAccessToken, newRefreshToken = resp['access'], resp['refresh']

    # old access do not work
    invalidResp = requests.get(
        f'{url}/whoami',
        headers = { 'authorization': f'Bearer {accessToken}' }
    )
    assert invalidResp.status_code == 400
    assert_that(invalidResp.json()).is_equal_to({ 'error': 'Wrong token' })

    # old refresh do not work
    invalidResp = requests.post(
        f'{url}/refresh',
        headers = { 'authorization': f'Bearer {refreshToken}' }
    )
    assert invalidResp.status_code == 400
    assert_that(invalidResp.json()).is_equal_to({ 'error': 'Wrong token' })


    resp = requests.get(
        f'{url}/whoami',
        headers = { 'authorization': f'Bearer {newAccessToken}' }
    ).json()
    assert_that(resp).is_equal_to({ 'id': userId, 'login': 'loginTest' })