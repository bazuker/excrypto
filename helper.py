import math
import socket
import asyncio


class NoInternetException(Exception):
    pass


def internet(host="8.8.8.8", port=53, timeout=3):
    # Host: 8.8.8.8 (google-public-dns-a.google.com)
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        raise NoInternetException("not connected to the Internet")


# method must be an asynchronous function taking one parameter (item of the collection)
def async_list_task(method, collection):
    loop = asyncio.get_event_loop()
    [asyncio.ensure_future(method(x)) for x in collection]
    pending = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))


async def __load_markets_async(g):
    return await g.load_markets()


def load_markets(gateways):
    async_list_task(__load_markets_async, gateways)


def truncate(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper
