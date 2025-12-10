import asyncio
import json

import aiohttp


urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
    "https://github.com",
    "https://yandex.ru",
    "https://career.habr.com",
    "https://www.duckdns.org",
    "https://stackoverflow.com",
]


async def fetch_urls(urls: list[str], file_path: str):
    semaphore = asyncio.Semaphore(5)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_url_with_semaphore(session, url, semaphore) for url in urls]

        results = await asyncio.gather(*tasks)

    with open(file_path, 'w', encoding='utf-8') as file:
        for url, status_code in results:
            result_dict = {url: status_code}
            file.write(json.dumps(result_dict)+'\n')

async def fetch_url_with_semaphore(session, url, semaphore):
    print(f"Getting: {url}")
    async with semaphore:
        try:
            async with session.get(url) as response:
                return url, response.status
        except asyncio.TimeoutError:
            return url, 0
        except aiohttp.ClientError:
            return url, 0
        except Exception:
            return url, 0

if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.jsonl'))
