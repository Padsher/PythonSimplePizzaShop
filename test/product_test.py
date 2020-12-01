import requests
from assertpy import assert_that
from serverParams import url
from common import clearDatabase, registerUser
from repository.DatabaseClient import databaseClient

def test_get_products():
    clearDatabase()
    resp = requests.get(f'{url}/product', json = {}).json()

    expectedResp = [
        {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '12.07'},
        {'id': 2, 'name': 'pepperoni', 'picture': 'pepperoni.png', 'price': '10.75'},
        {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26'},
        {'id': 4, 'name': 'americana', 'picture': 'americana.png', 'price': '13.99'},
        {'id': 5, 'name': 'four cheeses', 'picture': 'four_cheeses.png', 'price': '12.5'},
        {'id': 6, 'name': 'hawaiian', 'picture': 'hawaiian.png', 'price': '14.25'},
        {'id': 7, 'name': 'neopolitano', 'picture': 'neopolitana.png', 'price': '17.32'},
        {'id': 8, 'name': 'diablo', 'picture': 'diablo.png', 'price': '23.99'}
    ]

    assert_that(resp).is_equal_to(expectedResp)

def test_get_products_with_currency():
    clearDatabase()
    resp = requests.get(f'{url}/product', json = { 'currency': 'RUB' }).json()
    print(resp)
    expectedResp = [
        {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '936.3906'},
        {'id': 2, 'name': 'pepperoni', 'picture': 'pepperoni.png', 'price': '833.985'},
        {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '873.5508'},
        {'id': 4, 'name': 'americana', 'picture': 'americana.png', 'price': '1085.3442'},
        {'id': 5, 'name': 'four cheeses', 'picture': 'four_cheeses.png', 'price': '969.75'},
        {'id': 6, 'name': 'hawaiian', 'picture': 'hawaiian.png', 'price': '1105.515'},
        {'id': 7, 'name': 'neopolitano', 'picture': 'neopolitana.png', 'price': '1343.6856'},
        {'id': 8, 'name': 'diablo', 'picture': 'diablo.png', 'price': '1861.1442'}
    ]

    assert_that(resp).is_equal_to(expectedResp)

def test_get_products_with_filter():
    clearDatabase()

    # name filter
    resp = requests.get(f'{url}/product', json = { 'name': 'na' }).json()
    expectedResp = [
        {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26'},
        {'id': 4, 'name': 'americana', 'picture': 'americana.png', 'price': '13.99'}
    ]
    assert_that(resp).is_equal_to(expectedResp)

    # price filter
    resp = requests.get(f'{url}/product', json = { 'minPrice': 11.02, 'maxPrice': 14.05 }).json()
    expectedResp = [
        {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '12.07'},
        {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '11.26'},
        {'id': 4, 'name': 'americana', 'picture': 'americana.png', 'price': '13.99'},
        {'id': 5, 'name': 'four cheeses', 'picture': 'four_cheeses.png', 'price': '12.5'}
    ]
    assert_that(resp).is_equal_to(expectedResp)

    # price filter with currency
    resp = requests.get(
        f'{url}/product',
        json = { 'minPrice': 854.93, 'maxPrice': 1089.99, 'currency': 'RUB' }
    ).json()
    expectedResp = [
        {'id': 1, 'name': 'margarita', 'picture': 'margarita.png', 'price': '936.3906'},
        {'id': 3, 'name': 'carbonara', 'picture': 'carbonara.png', 'price': '873.5508'},
        {'id': 4, 'name': 'americana', 'picture': 'americana.png', 'price': '1085.3442'},
        {'id': 5, 'name': 'four cheeses', 'picture': 'four_cheeses.png', 'price': '969.75'}
    ]
    assert_that(resp).is_equal_to(expectedResp)
