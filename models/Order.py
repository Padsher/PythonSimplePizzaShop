from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List, Dict
from enum import Enum

@dataclass
class Order:
    id: int
    address: str
    name: str
    surname: str
    status: 'Order.Status'
    products: 'List[Order.ProductInfo]'
    shippingPrice: Decimal
    userId: Optional[str] = None

    class Status(Enum):
        NEW = 'New order'
        IN_PROGRESS = 'Order is in progress'
        FINISHED = 'Order is finished'

    @dataclass
    class ProductInfo:
        id: int
        name: int
        picture: str
        price: Decimal
        amount: int

        def toDict(self) -> dict:
            return {
                'id': self.id, 'name': self.name,
                'picture': self.picture, 'price': str(self.price),
                'amount': self.amount
            }

    def toDict(self) -> dict:
        return {
            'id': self.id, 'userId': self.userId, 'address': self.address,
            'name': self.name, 'surname': self.surname, 'status': self.status.value,
            'products': [p.toDict() for p in self.products],
            'shippingPrice': str(self.shippingPrice)
        }
    
    @dataclass
    class CreateInfo:
        address: str
        name: str
        surname: str
        products: Dict[int, int] # dict { productId: amount }
        shippingPrice: Decimal
        userId: Optional[int] = None
