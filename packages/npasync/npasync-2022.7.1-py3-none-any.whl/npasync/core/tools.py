import asyncio
import json
from typing import Dict, List, Optional, Tuple, Union

from aiohttp import ClientSession


class NPAsync(object):
    def __init__(self) -> None:
        pass

    def request_get(self, urls: List) -> List:
        method = "get"
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.make_requests(urls))
        x = loop.run_until_complete(future)
        return x

    async def fetch(
        self, url: str, session: ClientSession, index: int
    ) -> Tuple[Dict, int]:
        async with session.get(url) as response:
            return await response.json(), index

    async def make_requests(self, urls: List):
        tasks = []
        async with ClientSession() as session:
            for i, url in enumerate(urls):
                callback_key = i
                task = asyncio.ensure_future(
                    self.fetch(url, session, callback_key)
                )
                tasks.append(task)
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses


if __name__ == "__main__":
    n = NPAsync()
    base_url = "https://pokeapi.co/api/v2/pokemon/{}"
    urls = [base_url.format(x) for x in range(1, 21)]
    output = n.request_get(urls=urls)
    print(f"Total output is: {len(output)}")
    print(f"Showing the name of each Pokemon(parsed)")
    for item in output:
        print(f"{item[0]['name']}")
