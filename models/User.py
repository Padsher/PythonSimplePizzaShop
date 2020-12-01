from dataclasses import dataclass

@dataclass
class User:
    id: int
    login: str

    def toDict(self) -> dict:
        return { 'id': self.id, 'login': self.login }