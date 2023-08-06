from limiter import *
from asyncio import *
import asyncio
import logging


logging.basicConfig(level=0)
limiter = Limiter(rate=1.1, capacity=11)


@limiter(consume=5)
async def ex(*args, **kwargs):
    print(*args, **kwargs)

await gather(*map(ex, range(10)))
