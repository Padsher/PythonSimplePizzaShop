import re
from aiohttp import web
from routes.routes import routes
from routes.exceptions import ClientException, NotAuthorizedException
from auth.AuthenticationManager import authenticationManager

tokenPattern = re.compile(r'^Bearer (.*)$')

@routes.post('/register')
async def registerUser(request):
    try:
        body = await request.json()
    except Exception:
        raise ClientException('No body')

    login = body.get('login', '')
    password = body.get('password', '')
    if login == '': raise ClientException('Login is empty')
    if password == '': raise ClientException('Password is empty')

    tokens = await authenticationManager.registerUser(login, password)
    return web.json_response(tokens)

@routes.post('/login')
async def loginUser(request):
    try:
        body = await request.json()
    except Exception:
        raise ClientException('No body')
    
    login = body.get('login', '')
    password = body.get('password', '')
    if login == '': raise ClientException('Login is empty')
    if password == '': raise ClientException('Password is empty')

    tokens = await authenticationManager.loginUser(login, password)
    if tokens is None:
        raise ClientException('Invalid credentials')
    return web.json_response(tokens)

@routes.post('/refresh')
async def refreshUserSession(request):
    tokenRaw = request.headers['authorization']
    token = tokenPattern.findall(tokenRaw)
    if len(token) == 0: raise NotAuthorizedException()
    token = token[0]
    try:
        tokens = await authenticationManager.refreshSession(token)
    except Exception:
        raise ClientException('Wrong token')

    return web.json_response(tokens)

@routes.get('/whoami')
async def getUser(request):
    if request.user is None:
        return web.json_response({})
    else:
        return web.json_response(request.user.toDict())
