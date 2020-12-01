import os
RUN_ENV = os.getenv('RUN_ENV') or 'dev'

HOST = 'localhost'
PORT = 5432
USERNAME = 'pizza'
PASSWORD = 'pizza'

# this must be on whole config but I wrote it only to show
DATABASE = { 'test': 'pizza_test', 'dev': 'pizza_test_dev' }[RUN_ENV]