import asyncio
from typing import Optional
import requests
from requests import Request, Session, PreparedRequest, Response
from serverParams import url
from repository.DatabaseClient import databaseClient, DatabaseClient

def clearDatabase():
    coro = databaseClient.execute("""
        TRUNCATE users; TRUNCATE sessions;
        TRUNCATE orders; TRUNCATE order_product_link;
    """)
    asyncio.get_event_loop().run_until_complete(coro)

def registerUser(login: str, password: str) -> int:
    requests.post(f'{url}/register', json = { 'login': login, 'password': password })
    coro = databaseClient.query(f"""
        SELECT id FROM users WHERE login = '{login}'
    """)
    result = asyncio.get_event_loop().run_until_complete(coro)
    return result[0][0]

class RequestAuthorized:
    def _setToken(self) -> dict:
        resp = requests.post(
            f'{url}/login',
            json = { 'login': self.login, 'password': self.password }
        ).json()
        self.accessToken = resp['access']

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self._setToken()
    
    def _sendWithToken(self, request: PreparedRequest) -> Response:
        request.headers['authorization'] = f'Bearer {self.accessToken}'
        return Session().send(request)
    
    def _tryWithTokenAndRelogin(self, request: PreparedRequest) -> Response:
        resp = self._sendWithToken(request)
        if resp.status_code == 200:
            return resp

        self._setToken()
        return self._sendWithToken(request)

    def get(self, url: str, json: Optional[dict] = None) -> Response:
        request = Request('GET', url, json = json)
        return self._tryWithTokenAndRelogin(request.prepare())
    
    def post(self, url: str, json: Optional[dict] = None) -> Response:
        request = Request('POST', url, json = json)
        return self._tryWithTokenAndRelogin(request.prepare())

class BlockingDatabaseClient:
    def __init__(self, databaseClient: DatabaseClient):
        self.db= databaseClient

    def query(self, sql):
        return asyncio.get_event_loop().run_until_complete(self.db.query(sql))
    
    def execute(self, sql):
        asyncio.get_event_loop().run_until_complete(self.db.execute(sql))
    
blockingDatabaseClient = BlockingDatabaseClient(databaseClient)