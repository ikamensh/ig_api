import os
import sys


root = os.path.dirname(__file__)
data_folder = os.path.join(root, "data")
persistence_folder = os.path.join(root, "persistence")

os.makedirs(persistence_folder, exist_ok=True)
os.makedirs(data_folder, exist_ok=True)

src_folder = os.path.join(root, "src")
sys.path.append(src_folder)


from loguru import logger
import requests

def wrap_request(foo):
    def _(*args, **kwargs):
        logger.debug(f"Calling requests.{foo.__name__} with {args=} and {kwargs=}")
        return foo(*args, **kwargs)

    return _

requests.get = wrap_request(requests.get)
requests.get = wrap_request(requests.post)
