import traceback
import json
import re
from aiohttp import web
from routes.exceptions import ClientException, NotAuthorizedException
from auth.AuthenticationManager import authenticationManager

tokenPattern = re.compile(r'^Bearer (.*)$')

@web.middleware
async def globalExceptionHandler(req, handler):
    try:
        return await handler(req)
    except ClientException as e:
        return web.Response(status = 400, text = json.dumps({ 'error': e.message}))
    except NotAuthorizedException:
        return web.Response(status = 401)
    except Exception as e:
        print("Unknown exception") # use simple prints instead of logger for this simple server
        print(e)
        traceback.print_tb(e.__traceback__)
        print()
        print(f'Req: {req.method} {req.path_qs}, body: {await req.text()}')
        return web.Response(status = 500)


@web.middleware
async def authMiddleware(request, handler):
    tokenRaw = request.headers.get('authorization', '')
    token = tokenPattern.findall(tokenRaw)
    token = token[0] if len(token) > 0 else None
    if token is None:
        request.user = None
    else:
        try:
            request.user = await authenticationManager.getUser(token)
        except Exception:
            raise ClientException('Wrong token')
    
    return await handler(request)


middlewares = [
    globalExceptionHandler, authMiddleware
]