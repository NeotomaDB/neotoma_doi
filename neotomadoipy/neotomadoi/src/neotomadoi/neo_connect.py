import psycopg2
from dotenv import dotenv_values
from json import loads

def neo_connect()->psycopg2.connect:
    """_Connect to the Neotoma Database_

    Args:
        connobj (object): _An object with properties DBNAME, etc._

    Returns:
        psycopg2.connect: _A valid connection the the Neotoma Database server_
    """    
    secrets = dotenv_values()
    CONN_STRING = loads(secrets['DBAUTH'])
    con = psycopg2.connect(**CONN_STRING, connect_timeout=5)
    return con
