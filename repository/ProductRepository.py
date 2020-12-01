from typing import Optional, Any, List
from dataclasses import dataclass, field
from decimal import Decimal
from pypika import Criterion, PostgreSQLQuery as Query, Field
from pypika.enums import JoinType
from repository.tables import products, currencies
from repository.DatabaseClient import databaseClient
from models.Product import Product

class ProductRepository:
    async def getProducts(
        self, productFilter: 'ProductRepository.Filter', currency: str = 'USD' # yes, it is just hardcoded
    ) -> List[Product]:
        multiplier = await self.getCurrencyMultiplier(currency)
        if multiplier is None: raise Exception(f'No multiplier for currecncy {currency}')
        productFilter.applyMultiplier(multiplier)

        sql = Query.from_(products) \
            .select(
                products.id, products.name, products.picture,
                (products.price_dollar * multiplier).as_('price')
            ).where(productFilter.getCriterion()) \
                .limit(productFilter.limit).offset(productFilter.offset)

        result = await databaseClient.query(sql.get_sql())
        return [
            Product(
                id = row[0], name = row[1], picture = row[2],
                price = row[3].normalize()
            ) for row in result
        ]

    async def getCurrencyMultiplier(sefl, currency: str) -> Optional[Decimal]:
        sql = Query.from_(currencies).select(currencies.multiplier) \
            .where(currencies.currency == currency)
        
        result = await databaseClient.query(sql.get_sql())
        if len(result) == 0: return None
        return result[0][0]

    @dataclass
    class Filter:
        id: List[int] = field(default_factory = list)
        name: Optional[str] = None
        minPrice: Optional[Decimal] = None
        maxPrice: Optional[Decimal] = None
        limit: int = 10
        offset: int = 0

        def getCriterion(self):
            conds = []
            if self.name is not None: conds.append(products.name.ilike(f'%{self.name}%'))
            if len(self.id) != 0: conds.append(products.id.isin(self.id))
            if self.minPrice is not None: conds.append(products.price_dollar >= self.minPrice)
            if self.maxPrice is not None: conds.append(products.price_dollar <= self.maxPrice)
            return Criterion.all(conds)
        
        def applyMultiplier(self, multiplier: Decimal):
            if self.minPrice is not None:
                self.minPrice = Decimal(self.minPrice) / multiplier
            
            if self.maxPrice is not None:
                self.maxPrice = Decimal(self.maxPrice) / multiplier

productRepository = ProductRepository()