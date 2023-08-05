from netdot import client as Client
from netdot.dataclasses import *
from netdot.repository import Repository, T

# Enable `netdot.connect()` to interactively set up a NetdotRepository
connect = Repository.connect

__version__ = '0.2.1'
__all__ = [
    'Client',
    'connect',
    'Repository', 
    'T',
    '__version__',
]
