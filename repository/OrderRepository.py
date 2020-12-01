from dataclasses import dataclass, field
from typing import Optional, List
from pypika import Criterion, PostgreSQLQuery as Query
from pypika.functions import Cast
from pypika.terms import AggregateFunction
from models.Order import Order
from models.User import User
from repository.tables import orders, order_product_link, products
from repository.ProductRepository import productRepository
from repository.DatabaseClient import databaseClient, DatabaseClient

class OrderRepository:
    async def _getOrders(self, orderFilter: 'OrderRepository.Filter', currency: str) -> List[Order]:
        multiplier = await productRepository.getCurrencyMultiplier(currency)
        if multiplier is None: raise Exception(f'Invalid currency {currency}')

        # implementing select with M2M using aggregation instead of subquery
        # so use raw SQL
        sql = f"""
            SELECT
                orders.id, min(orders.user_id), min(orders.name), min(orders.surname),
                min(orders.status)::text, min(orders.shipping_price) * {multiplier}, min(orders.address),

                json_agg(json_build_object(
                    'id', products.id, 'name', products.name, 'picture', products.picture,
                    'price', products.price_dollar * {multiplier}, 'amount', order_product_link.amount
                ))
            FROM orders
            JOIN order_product_link ON orders.id = order_product_link.order_id
            JOIN products ON order_product_link.product_id = products.id
            {orderFilter.getRawCond()}
            GROUP BY orders.id
            ORDER BY orders.id ASC
            LIMIT {orderFilter.limit}
            OFFSET {orderFilter.offset}
        """

        result = await databaseClient.query(sql)
        return [
            Order(
                id = row[0], userId = row[1], name = row[2], surname = row[3],
                status = Order.Status[row[4]], shippingPrice = row[5].normalize(), address = row[6],
                products = [self._productInfoFromDict(prod) for prod in row[7]]
            ) for row in result
        ]
    
    def _productInfoFromDict(self, product: dict) -> Order.ProductInfo:
        return Order.ProductInfo(
            id = product['id'], name = product['name'], picture = product['picture'],
            price = product['price'], amount = product['amount']
        )
    
    async def getUserOrders(self, userId: int, limit = 10, offset = 0, currency: str = 'USD') -> List[Order]:
        orderFilter = self.Filter(userId = userId, limit = limit, offset = offset)
        return await self._getOrders(orderFilter, currency)
    
    async def getOrderById(self, orderId: int, currency: str = 'USD') -> Order:
        orderFilter = self.Filter(id = [orderId])
        result = await self._getOrders(orderFilter, currency)
        if len(result) == 0: return None
        return result[0]

    @dataclass
    class Filter:
        id: List[int] = field(default_factory = list)
        userId: Optional[int] = None
        limit: int = 10
        offset: int = 0

        def getRawCond(self) -> str:
            conds = []
            if self.userId is not None: conds.append(f'orders.user_id = {self.userId}')
            if len(self.id) != 0:
                conds.append(
                    f"orders.id IN ({','.join([str(id) for id in self.id])})"
                )
            if len(conds) == 0: return ""
            return f"WHERE {' AND '.join(conds)}"
    
    async def createOrder(self, order: Order.CreateInfo) -> int:
        if len(order.products) == 0: raise Exception('No products')

        orderSql = Query.into(orders).columns(
            orders.address, orders.name, orders.surname, orders.user_id,
            orders.status, orders.shipping_price
        ).insert(
            order.address, order.name, order.surname, order.userId,
            Cast('NEW', 'ORDER_STATUS'), order.shippingPrice
        ).returning(orders.id)

        productsSql = Query.into(order_product_link).columns(
            order_product_link.order_id, order_product_link.product_id, order_product_link.amount
        )

        async with databaseClient.transaction() as t:
            orderId = (await t.query(orderSql.get_sql()))[0][0]
            for prodId, amount in order.products.items():
                productsSql = productsSql.insert(orderId, prodId, amount)
            await t.execute(productsSql.get_sql())

        return orderId

orderRepository = OrderRepository()