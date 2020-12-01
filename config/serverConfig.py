import os
from decimal import Decimal
RUN_ENV = os.getenv('RUN_ENV') or 'dev'

PORT = { 'dev': 8080, 'test': 34567 }[RUN_ENV]
PASS_HASH_SECRET = 'very secret'
JWT_SECRET = 'jwt secret'
JWT_ACCESS_TTL = 60 * 5 # in seconds (5 minutes)
JWT_REFRESH_TTL = 60 * 60 * 24 # in seconds (1 day)
SHIPPING_PRICE = Decimal(15.43) # just store all in one config, in dollars by the way