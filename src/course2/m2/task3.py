import redis
import random
import time
import uuid

class RateLimitExceed(Exception):
    pass

class RateLimiter:
    def __init__(self, redis_client=None, key='rate_limit:default', limit=5, window=3):
        """
        Инициализирует RateLimiter.

        :param redis_client: Экземпляр redis.Redis. Если None, создается новый.
        :param key: Уникальный ключ для хранения данных лимитера в Redis.
        :param limit: Максимальное количество запросов за окно времени.
        :param window: Размер окна времени в секундах.
        """
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.key = key
        self.limit = limit
        self.window = window

    def test(self) -> bool:
        """
        Проверяет, можно ли выполнить запрос в данный момент.

        :return: True, если лимит не превышен, False - если превышен.
        """
        current_time = time.time()
        
        window_start_time = current_time - self.window

        # 1. Удаляем все элементы, которые находятся за пределами окна (старше 3 секунд)
        # ZREMRANGEBYSCORE удаляет элементы с оценкой в заданном диапазоне
        self.redis_client.zremrangebyscore(self.key, 0, window_start_time)

        # 2. Подсчитываем количество оставшихся элементов (запросов за последние 3 секунды)
        current_requests_count = self.redis_client.zcard(self.key)

        # 3. Проверяем, не превышен ли лимит
        if current_requests_count >= self.limit:
            # Лимит превышен
            return False

        # 4. Лимит не превышен, добавляем текущий запрос
        # Создаем уникальный идентификатор для этого запроса
        request_id = str(uuid.uuid4())
        # Добавляем в Sorted Set: идентификатор запроса и его временную метку
        # ZADD добавит, если ключа не существует, или обновит оценку, если существует
        self.redis_client.zadd(self.key, {request_id: current_time})

        # 5. Возвращаем True, так как запрос разрешен
        return True

def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        # time.sleep(0.1) # Имитация работы API
        pass

if __name__ == '__main__':
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
