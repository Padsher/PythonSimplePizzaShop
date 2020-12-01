import asyncio
import aiopg
from contextlib import asynccontextmanager
from config.databaseConfig import HOST, PORT, USERNAME, PASSWORD, DATABASE

class DatabaseClient:
    def __init__(self):
        dsn = f'dbname={DATABASE} user={USERNAME} password={PASSWORD} host={HOST} port={PORT}'
        self.pool = asyncio.get_event_loop().run_until_complete(aiopg.create_pool(dsn))

    async def query(self, sql):
        result = []
        with (await self.pool.cursor()) as cur:
            await cur.execute(sql)
            result = await cur.fetchall()

        return result
    
    async def execute(self, sql):
         with (await self.pool.cursor()) as cur:
            await cur.execute(sql)
    
    @asynccontextmanager
    async def transaction(self):
        with (await self.pool.cursor()) as cur:
            await cur.execute('BEGIN')
            try:
                yield self.Transaction(cur)
                await cur.execute('COMMIT')
            except Exception as e:
                await cur.execute('ROLLBACK')
                raise e
        
    class Transaction:
        def __init__(self, cursor):
            self.cursor = cursor
        
        async def execute(self, sql):
            await self.cursor.execute(sql)
        
        async def query(self, sql):
            await self.cursor.execute(sql)
            return await self.cursor.fetchall()

databaseClient = DatabaseClient()