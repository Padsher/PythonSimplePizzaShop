import os
import time
import requests
from subprocess import Popen, PIPE

serverProcess = None
os.environ['RUN_ENV'] = 'test'
from serverParams import url

# there we start our server before all tests
def pytest_configure(config):
    global serverProcess
    serverProcess = Popen(
        'exec python3 main.py',
        cwd = os.getcwd(), env = os.environ, shell = True
    )
    while True: # waiting for server to work
        try:
            print(requests.get(f'{url}/whoami'))
            break
        except Exception:
            pass
    
# and there we stop it after
def pytest_unconfigure(config):
    print('Unconfigure fun')
    serverProcess.kill()