import hmac
import hashlib
import base64
from typing import Optional
from datetime import datetime, timezone
from pypika import Criterion, PostgreSQLQuery as Query
from repository.tables import users, sessions
from repository.DatabaseClient import databaseClient
from config.serverConfig import PASS_HASH_SECRET
from models.User import User
from models.Session import Session

class UserRepository:
    def _getPasswordHash(self, password: str) -> str:
        dig = hmac.new(
            PASS_HASH_SECRET.encode(),
            msg=password.encode(),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()


    async def createUser(self, login: str, password: str) -> int:
        sql = Query.into(users).columns(users.login, users.password_hash) \
            .insert(login, self._getPasswordHash(password)) \
            .returning(users.id)
        
        result = await databaseClient.query(sql.get_sql())
        return result[0][0]
    
    async def checkUser(self, login: str, password: str) -> Optional[int]:
        sql = Query.from_(users).select(users.id) \
            .where(Criterion.all([
                users.login == login,
                users.password_hash == self._getPasswordHash(password)
            ]))
                
        result = await databaseClient.query(sql.get_sql())
        if len(result) == 0: return None
        return result[0][0]
    
    async def getUserById(self, id: int) -> Optional[User]:
        sql = Query.from_(users).select(users.id, users.login).where(users.id == id)
        result = await databaseClient.query(sql.get_sql())
        
        if len(result) == 0: return None
        row = result[0]
        return User(id = row[0], login = row[1])
    
    async def insertSession(self, userId: int) -> Session:
        sql = Query.into(sessions).columns(sessions.user_id, sessions.updated_at) \
            .insert(userId, datetime.now(timezone.utc)) \
            .returning(sessions.session_id, sessions.user_id, sessions.updated_at)
        
        result = await databaseClient.query(sql.get_sql())
        row = result[0]
        return Session(sessionId = row[0], userId = row[1], updatedAt = row[2])
    
    async def refreshSession(self, session: Session) -> Optional[Session]:
        sql = Query.update(sessions).set(sessions.updated_at, datetime.now(timezone.utc)) \
            .where(Criterion.all([
                sessions.session_id == session.sessionId,
                sessions.user_id == session.userId,
                sessions.updated_at == session.updatedAt
            ])) \
            .returning(sessions.session_id, sessions.user_id, sessions.updated_at)

        result = await databaseClient.query(sql.get_sql())
        if len(result) == 0: return None
        row = result[0]
        return Session(sessionId = row[0], userId = row[1], updatedAt = row[2])
    
    async def checkSession(self, session: Session) -> bool:
        sql = Query.from_(sessions).select(sessions.user_id) \
            .where(Criterion.all([
                sessions.session_id == session.sessionId,
                sessions.user_id == session.userId,
                sessions.updated_at == session.updatedAt
            ]))
        
        result = await databaseClient.query(sql.get_sql())
        return len(result) > 0

userRepository = UserRepository() # make singleton with module caching
    