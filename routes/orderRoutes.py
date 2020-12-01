from aiohttp import web
from routes.routes import routes
from routes.exceptions import ClientException, NotAuthorizedException
from repository.OrderRepository import orderRepository, OrderRepository
from models.Order import Order
from config.serverConfig import SHIPPING_PRICE

@routes.get('/order')
async def getOrders(request):
    try:
        body = await request.json()
    except Exception:
        raise ClientException('No body, use {} if no filter option specified')

    if request.user is None:
        raise NotAuthorizedException()

    currency = body.get('currency', 'USD')
    limit = body.get('limit', 10)
    offset = body.get('offset', 0)

    orders = await orderRepository.getUserOrders(request.user.id, limit, offset, currency)
    return web.json_response([o.toDict() for o in orders])

@routes.post('/order')
async def createOrder(request):
    try:
        body = await request.json()
    except Exception:
        raise ClientException('No body, use {} if no filter option specified')
    body = validateCreateOrderBody(body)
    createInfo = Order.CreateInfo(
        address = body['address'], name = body['name'], surname = body['surname'],
        products = body['products'], shippingPrice = SHIPPING_PRICE,
        userId = request.user.id if request.user is not None else None
    )

    orderId = await orderRepository.createOrder(createInfo)
    return web.json_response({ 'id': orderId })

def validateCreateOrderBody(body: dict) -> dict:
    (address, name, surname, products) = (
        body.get('address', None), body.get('name', None),
        body.get('surname', None), body.get('products', None)
    )

    if not isinstance(address, str): raise ClientException('Invalid address')
    if not isinstance(name, str): raise ClientException('Invalid name')
    if not isinstance(surname, str): raise ClientException('Invalid surname')
    if not isinstance(products, dict): raise ClientException('Invalid products')
    newProducts = {}
    for k, v in products.items():
        try:
            newK = int(k)
            newV = int(v)
        except Exception:
            raise ClientException(f'Invalid product {k}: {v}')

        newProducts[newK] = newV
    
    body['products'] = newProducts

    # body will be passed by reference, so there is no need to return
    # but I would like not to use such changing by reference magic
    # when function is called and argument is changed now, because it is not method
    return body




    