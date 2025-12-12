import asyncio
import json
import aiohttp
from uvicorn import run

async def currency_app(scope, receive, send):
    if scope['type'] != 'http':
        raise ValueError("Scope type must be 'http'")

    path = scope['path'].strip('/')
    if not path:
        currency_code = 'USD'
    else:
        currency_code = path.upper()

    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{currency_code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    response_data = await response.json()
                    await send_response(send, 200, response_data)
                else:
                    error_message = {"error": f"Currency {currency_code} not found or API error"}
                    await send_response(send, response.status, error_message)

    except aiohttp.ClientError as e:
        # Ошибка подключения (например, нет интернета)
        error_message = {"error": f"Could not connect to API: {e}"}
        await send_response(send, 502, error_message)

    except Exception as e:
        # Обработка других ошибок
        error_message = {"error": "Internal server error"}
        await send_response(send, 500, error_message)

async def send_response(send, status_code: int, response_data: dict):
    """Вспомогательная функция для отправки JSON-ответа."""
    response_body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [
            [b'content-type', b'application/json'],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': response_body,
    })


# Точка входа для Uvicorn
app = currency_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("task1:app", host="0.0.0.0", port=8000, reload=True)