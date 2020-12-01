from pypika import Schema

public = Schema('public')
users = public.users
sessions = public.sessions
products = public.products
currencies = public.currencies
orders = public.orders
order_product_link = public.order_product_link
