import asyncio
import glob
from repository.DatabaseClient import databaseClient

# Use the simplest migration, which are '... IF NOT EXIST...'
# for use on every launch, in real product there may be some migration tool
# like yo-yo migration, or django migrations
migrationFiles = [f for f in glob.glob('./migrations/*.sql')]
migrationFiles.sort()
print(migrationFiles)
for migrationFile in migrationFiles:
    try:
        with open(migrationFile) as migration:
            text = migration.read()
            coro = databaseClient.execute(text)
            asyncio.get_event_loop().run_until_complete(coro)
    except Exception as e:
        print(f'Error occured while migrating {migrationFile}')
        print(e)