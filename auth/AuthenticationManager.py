import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional
from config.serverConfig import JWT_SECRET, JWT_ACCESS_TTL, JWT_REFRESH_TTL
from repository.UserRepository import userRepository
from models.User import User
from models.Session import Session

ACCESS_TIMEDELTA = timedelta(seconds = JWT_ACCESS_TTL)
REFRESH_TIMEDELTA = timedelta(seconds = JWT_REFRESH_TTL)

class AuthenticationManager:
    def _createTokens(self, session: Session) -> dict:
        now = datetime.now(timezone.utc)
        accessExp = now + ACCESS_TIMEDELTA
        refreshExp = now + REFRESH_TIMEDELTA
        return {
            'access': jwt.encode(
                { 'exp': accessExp, 'type': 'ACCESS', 'session': session.toDict() },
                JWT_SECRET,
                algorithm='HS256'
            ).decode(),
            'refresh': jwt.encode(
                { 'exp': refreshExp, 'type': 'REFRESH','session': session.toDict() },
                JWT_SECRET,
                algorithm='HS256'
            ).decode()
        }
    
    async def registerUser(self, login: str, password: str) -> dict:
        userId = await userRepository.createUser(login, password)
        return await self.loginUser(login, password)

    async def loginUser(self, login: str, password: str) -> Optional[dict]:
        userId = await userRepository.checkUser(login, password)
        if userId is None: return

        session = await userRepository.insertSession(userId)
        return self._createTokens(session)
    
    async def getUser(self, accessToken: str) -> Optional[User]:
        info = jwt.decode(accessToken, JWT_SECRET, algorithms=['HS256'])
        if info['type'] != 'ACCESS': return None

        session = Session.fromDict(info['session'])
        if (await userRepository.checkSession(session)):
            return await userRepository.getUserById(session.userId)
        else:
            raise Exception('Wrong token')
    
    async def refreshSession(self, refreshToken: str) -> dict:
        info = jwt.decode(refreshToken, JWT_SECRET, algorithms=['HS256'])
        if info['type'] != 'REFRESH': raise Exception('Not refresh token')

        session = Session.fromDict(info['session'])
        newSession = await userRepository.refreshSession(session)
        if newSession is None: raise Exception('Wrong token')
        return self._createTokens(newSession)

authenticationManager = AuthenticationManager()
