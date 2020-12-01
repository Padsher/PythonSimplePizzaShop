from decimal import Decimal
import requests
from assertpy import assert_that
from serverParams import url
from common import clearDatabase, registerUser, RequestAuthorized, blockingDatabaseClient

def test_create_order():
    clearDatabase()
    resp = requests.post(
        f'{url}/order',
        json = {
            'address': 'Lenina street', 'name': 'James', 'surname': 'Bond',
            'products': { 1: 2, 3: 1 }
        }
    ).json()
    orderId = resp['id']

    result = blockingDatabaseClient.query(f"""
        SELECT id, user_id, address, name, surname, status, shipping_price
        FROM public.orders
        WHERE id = {orderId}
    """)
    expectedResult = [(orderId, None, 'Lenina street', 'James', 'Bond', 'NEW', Decimal('15.4300000000'))]
    assert_that(result).is_equal_to(expectedResult)

    result = blockingDatabaseClient.query(f"""
        SELECT order_id, product_id, amount FROM order_product_link
        WHERE order_id = {orderId}
    """)
    expectedResult = [(orderId, 1, 2), (orderId, 3, 1)]
    assert_that(result).is_equal_to(expectedResult)

def test_create_order_authorized():
    clearDatabase()
    userId = registerUser('test', 'test_pass')
    requestAuthorized = RequestAuthorized('test', 'test_pass')
    resp = requestAuthorized.post(
        f'{url}/order',
        json = {
            'address': 'Lenina street', 'name': 'James', 'surname': 'Bond',
            'products': { 1: 2, 3: 1 }
        }
    ).json()
    orderId = resp['id']

    result = blockingDatabaseClient.query(f"""
        SELECT id, user_id, address, name, surname, status, shipping_price
        FROM public.orders
        WHERE id = {orderId}
    """)
    expectedResult = [(orderId, userId, 'Lenina street', 'James', 'Bond', 'NEW', Decimal('15.4300000000'))]
    assert_that(result).is_equal_to(expectedResult)

def test_get_orders():
    clearDatabase()
    userId = registerUser('test', 'test_pass')
    requestAuthorized = RequestAuthorized('test', 'test_pass')

    bodies = [
        {
            'address': 'Lenina street', 'name': 'James', 'surname': 'Bond',
            'products': { 1: 2, 3: 1 }
        },
        {
            'address': 'Boulevard of broken dreams', 'name': 'Billy', 'surname': 'Joe',
            'products': { 2: 1, 3: 2 }
        },
        {
            'address': 'Street of Rage', 'name': 'Axel', 'surname': 'Blaze',
            'products': { 1: 1, 3: 2, 5: 3 }
        }
    ]

    orderIds = []

    for body in bodies:
        resp = requestAuthorized.post(f'{url}/order', json = body).json()
        orderIds.append(resp['id'])
    
    result = requestAuthorized.get(f'{url}/order', json = {}).json()
    expectedResult = [
        {
            'id': orderIds[0], 'userId': userId, 'address': 'Lenina street',
            'name': 'James', 'surname': 'Bond','status': 'New order',
            'products': [
                {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '12.07', 'amount': 2},
                {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26', 'amount': 1}
            ],
            'shippingPrice': '15.43'
        },
        {
            'id': orderIds[1], 'userId': userId, 'address': 'Boulevard of broken dreams',
            'name': 'Billy', 'surname': 'Joe', 'status': 'New order',
            'products': [
                {'id': 2, 'name': 'pepperoni', 'picture': 'pepperoni.png', 'price': '10.75', 'amount': 1},
                {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26', 'amount': 2}
            ],
            'shippingPrice': '15.43'
        },
        {
            'id': orderIds[2], 'userId': userId, 'address': 'Street of Rage',
            'name': 'Axel', 'surname': 'Blaze','status': 'New order',
            'products': [
                {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '12.07', 'amount': 1},
                {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26', 'amount': 2},
                {'id': 5, 'name': 'four cheeses', 'picture': 'four_cheeses.png', 'price': '12.5', 'amount': 3}
            ],
            'shippingPrice': '15.43'
        }
    ]
    assert_that(result).is_equal_to(expectedResult)

    # test unauthorized
    invalidResp = requests.get(f'{url}/order', json = {})
    assert invalidResp.status_code == 401

def test_get_orders_with_currency():
    clearDatabase()
    userId = registerUser('test', 'test_pass')
    requestAuthorized = RequestAuthorized('test', 'test_pass')

    bodies = [
        {
            'address': 'Lenina street', 'name': 'James', 'surname': 'Bond', 'products': { 1: 2 }
        },
        {
            'address': 'Boulevard of broken dreams', 'name': 'Billy', 'surname': 'Joe', 'products': { 2: 1 }
        }
    ]
    orderIds = []
    for body in bodies:
        resp = requestAuthorized.post(f'{url}/order', json = body).json()
        orderIds.append(resp['id'])
    
    result = requestAuthorized.get(f'{url}/order', json = { 'currency': 'RUB' }).json()
    expectedResult = [
        {
            'id': orderIds[0], 'userId': userId, 'address': 'Lenina street',
            'name': 'James', 'surname': 'Bond', 'status': 'New order',
            'products': [
                {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '936.3906', 'amount': 2}
            ],
            'shippingPrice': '1197.0594'
        },
        {
            'id': orderIds[1], 'userId': userId, 'address': 'Boulevard of broken dreams',
            'name': 'Billy', 'surname': 'Joe', 'status': 'New order',
            'products': [
                {'id': 2, 'name': 'pepperoni', 'picture': 'pepperoni.png', 'price': '833.985', 'amount': 1}
            ],
            'shippingPrice': '1197.0594'
        }
    ]
    assert_that(result).is_equal_to(expectedResult)
