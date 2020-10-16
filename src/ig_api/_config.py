import os
import sys


root = os.path.dirname(__file__)
data_folder = os.path.join(root, "resources/data")
persistence_folder = os.path.join(root, "persistence")

os.makedirs(data_folder, exist_ok=True)

src_folder = os.path.join(root, "src")
sys.path.append(src_folder)


from loguru import logger
import requests

def wrap_request(foo):
    def _(*args, **kwargs):
        logger.opt(depth=1).debug(f"Calling requests.{foo.__name__} with {args=} and {kwargs=}")
        result: requests.Response = foo(*args, **kwargs)
        logger.opt(depth=1).debug(f"Response: {result.status_code=} {result.json()=}")
        return result

    return _

requests.get = wrap_request(requests.get)
requests.post = wrap_request(requests.post)
requests.delete = wrap_request(requests.delete)
requests.put = wrap_request(requests.put)
requests.patch = wrap_request(requests.patch)
