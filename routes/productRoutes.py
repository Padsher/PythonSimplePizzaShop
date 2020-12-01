from decimal import Decimal
from aiohttp import web
from routes.routes import routes
from routes.exceptions import ClientException
from repository.ProductRepository import productRepository, ProductRepository

@routes.get('/product')
async def getProducts(request):
    try:
        body = await request.json()
    except Exception:
        raise ClientException('No body')
    
    currency = body.get('currency', 'USD')
    
    prodFilter = ProductRepository.Filter(
        id = body.get('id', []), name = body.get('name', None),
        minPrice = body.get('minPrice', None), maxPrice = body.get('maxPrice', None),
        limit = body.get('limit', 10), offset = body.get('offset', 0)
    )

    products = await productRepository.getProducts(prodFilter, currency)
    return web.json_response([p.toDict() for p in products])