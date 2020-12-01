from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Product:
    id: int
    name: str
    picture: str
    price: Decimal

    def toDict(self) -> dict:
        return {
            'id': self.id, 'name': self.name,
            'picture': self.picture, 'price': f'{self.price}'
        }