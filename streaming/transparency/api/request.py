import aiohttp


async def fetch(client, url):
    async with client.get(url) as resp:
        return await resp.json()

async def async_request(url):
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=3600)
        async with aiohttp.ClientSession(timeout=timeout,
            connector=connector) as client:
            return await fetch(client, url)

    except Exception as err:
        print(err)
        return None


