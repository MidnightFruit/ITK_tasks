import redis
import json

class RedisQueue:
    def __init__(self, redis_client=None, queue_name='default_queue'):
        """
        Инициализирует очередь Redis.

        :param redis_client: Экземпляр redis.Redis. Если None, создается новый.
        :param queue_name: Имя ключа списка в Redis, представляющего очередь.
        """
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
        self.queue_name = queue_name

    def publish(self, msg: dict):
        """
        Добавляет сообщение в очередь.

        :param msg: Словарь, представляющий сообщение.
        """
        # Сериализуем словарь в строку JSON
        serialized_msg = json.dumps(msg)
        # LPUSH добавляет элемент в начало списка (левый конец)
        self.redis_client.lpush(self.queue_name, serialized_msg)

    def consume(self) -> dict:
        """
        Извлекает и возвращает сообщение из очереди.
        Блокирует выполнение до тех пор, пока не появится сообщение.

        :return: Словарь, представляющий сообщение.
        """
        # BRPOP блокирует выполнение до тех пор, пока не появится элемент
        # в одном из указанных ключей. Возвращает кортеж (ключ, значение).
        key, serialized_msg = self.redis_client.brpop(self.queue_name)
        # Десериализуем строку JSON обратно в словарь
        return json.loads(serialized_msg)


if __name__ == '__main__':
    q = RedisQueue()
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}

    print("Все тесты пройдены!")