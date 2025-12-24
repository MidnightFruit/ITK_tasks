import functools
import redis
import time
from datetime import timedelta
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def single(redis_client, max_processing_time: timedelta = timedelta(minutes=2)):
    """
    Декоратор для обеспечения одиночного (non-concurrent) выполнения функции
    в распределенной системе с использованием Redis.

    Использует redis.lock.Lock, который обеспечивает безопасное
    получение и освобождение блокировки.

    :param redis_client: Экземпляр клиента redis.Redis.
    :param max_processing_time: timedelta, максимальное время,
                                на которое устанавливается блокировка.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Создаем уникальный ключ для блокировки на основе имени функции
            lock_key = f"lock:{func.__name__}"
            
            # Создаем объект блокировки с помощью redis-py
            # lock_timeout = максимальное время выполнения функции
            # sleep = время ожидания между попытками получения блокировки
            # blocking = False, чтобы сразу вернуть None, если блокировка занята
            lock = redis_client.lock(
                lock_key,
                timeout=max_processing_time.total_seconds(), # Время жизни блокировки
                blocking=False, # Не ждем освобождения, сразу возвращаем результат
                thread_local=False # Для корректной работы в асинхронных/многопоточных средах
            )
            
            # Пытаемся получить блокировку
            if lock.acquire():
                logger.info(f"Acquired lock for function '{func.__name__}'. Starting execution.")
                try:
                    # Блокировка получена, выполняем функцию
                    result = func(*args, **kwargs)
                    logger.info(f"Function '{func.__name__}' completed successfully.")
                    return result
                except Exception as e:
                    logger.error(f"Function '{func.__name__}' raised an exception: {e}")
                    raise # Переподнимаем исключение
                finally:
                    # Обязательно освобождаем блокировку после выполнения или ошибки
                    # redis.lock.Lock.handle_release() гарантирует атомарность
                    try:
                        lock.release()
                        logger.info(f"Released lock for function '{func.__name__}'.")
                    except redis.exceptions.LockNotOwnedError:
                        # Произошло, если блокировка истекла до вызова release
                        logger.warning(f"Lock for function '{func.__name__}' was lost (likely expired) before release.")
                    except Exception as e:
                        logger.error(f"Error releasing lock for '{func.__name__}': {e}")
            else:
                # Не удалось получить блокировку, функция уже выполняется
                logger.info(f"Function '{func.__name__}' is already running on another instance. Skipping execution.")
                # Возвращаем None, как в предыдущих примерах
                return None 

        return wrapper
    return decorator

# --- Пример использования ---
if __name__ == "__main__":
    # Подключение к Redis (предполагается, что Redis запущен на localhost:6379)
    r_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    import datetime

    @single(r_client, max_processing_time=datetime.timedelta(seconds=10))
    def process_transaction():
        print("Начинаю обработку транзакции...")
        time.sleep(5) # Симуляция длительной работы
        print("Обработка транзакции завершена.")
        return "Success"

    # Пример запуска функции
    result = process_transaction()
    print(f"Результат выполнения: {result}")

    # Попробуем запустить еще раз вручную (или в другом процессе/экземпляре)
    # для демонстрации блокировки
    print("\nПопытка запустить снова...")
    result2 = process_transaction()
    print(f"Результат второго выполнения: {result2}")