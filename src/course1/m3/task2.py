import aiohttp
import asyncio
import json


async def fetch_urls(input_file: str, output_file: str = "result.jsonl", max_concurrent: int = 5) -> None:
    """Асинхронная загрузка URL из файла"""
    
    # Чтение URL
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_one(session: aiohttp.ClientSession, url: str) -> dict | None:
        async with semaphore:
            try:
                async with session.get(url, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {"url": url, "content": data}
            except Exception:
                pass
            return None
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    # Фильтрация успешных результатов
    successful = [r for r in results if r is not None]
    
    # Запись в файл
    with open(output_file, 'w') as f:
        for result in successful:
            f.write(json.dumps(result) + '\n')
    
    print(f"Успешно: {len(successful)}/{len(urls)}")


if __name__ == "__main__":
    import sys
    asyncio.run(fetch_urls(sys.argv[1] if len(sys.argv) > 1 else "urls.txt"))