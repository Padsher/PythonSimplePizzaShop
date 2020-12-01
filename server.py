import traceback
import json
from aiohttp import web
from config.serverConfig import PORT
from routes.all import routes
from routes.middlewares import middlewares


app = web.Application(middlewares = middlewares)
app.router.add_routes(routes)

async def startServer():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f'server started on {PORT}')