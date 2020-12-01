from dataclasses import dataclass
from datetime import datetime

@dataclass
class Session:
    sessionId: int
    userId: int
    updatedAt: datetime

    def toDict(self) -> dict:
        return {
            'id': self.sessionId,
            'userId': self.userId,
            'updatedAt': self.updatedAt.isoformat()
        }
    
    @classmethod
    def fromDict(cls, sessionDict: dict) -> 'Session':
        return cls(
            sessionId = sessionDict['id'],
            userId = sessionDict['userId'],
            updatedAt = datetime.fromisoformat(sessionDict['updatedAt'])
        )