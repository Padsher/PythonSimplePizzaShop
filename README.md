## Simple Pizza shop backend example
Tested on Python version 3.8.5

```
Simple pizza shop example on Python + PostgreSQL
Authorization, registration, few routes for products and orders
No admin API for product and user management
```

### Install dependencies
```
$ python -m pip install -r ./requirements.txt
```

### Configurate
```
./config/serverConfig
./config/databaseConfig

You can also determine config parameters for test
(It will be use when running pytest tests)
```

### Test
```
Firstly run test database, then migrate

$ export RUN_ENV=test
$ python migrate.py

Then run tests

$ python -m pytest

Do not run server before test, it will be run inside tests and closed after
```

### Run server
```
Firstly run main database, then migrate

$ python migrate.py

Then run server

$ python main.py
```