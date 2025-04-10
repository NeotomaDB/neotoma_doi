import datacite
from dotenv import load_dotenv
import os
import json

def datacite_client(test = True):
    """_Connect to the DataCite Python client_

    Args:
        test (bool, optional): _Are we using the DataCite sandbox?_. Defaults to True.

    Returns:
        _datacite.DataCiteRESTClient_: _The DataCite client._
    """
    load_dotenv()
    DATACITE = json.loads(os.getenv("DCITE"))
    if test:
        path = 'test'
    else:
        path = 'prod'
    try:
        client = datacite.DataCiteRESTClient(
            username = DATACITE.get('user'),
            password = DATACITE.get(path).get('pw'),
            prefix = DATACITE.get(path).get('handle'),
            test_mode = path == 'test'
        )
    except Exception as e:
        print(e)
    return client
