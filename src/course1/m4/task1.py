import random
from multiprocessing import Pool, Process, Queue
import concurrent.futures
import os
import time


def generate_data(n: int):
    result = []

    for i in range(n):
        result.append(random.randint(1, 1000))

    return result

def process_number(number: int):
    if number < 0:
        raise ValueError("Число не может быть отрицательным")
    
    factorial = 1

    for i in range(1, number + 1):
        factorial *= i
    
    return factorial

def concurrent_processing(n: int):

    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        numbers = executor.submit(generate_data, n).result()
        
        factorials = [executor.submit(process_number, i) for i in numbers]

        for factorial in concurrent.futures.as_completed(factorials):
            result.append(factorial.result())

    return result

def multiprocessing_pool_processing(n: int):
    result = []

    with Pool(os.cpu_count()) as pool:
        nums = generate_data(n)
        result = pool.map(process_number, nums)

    return result

def worker(input_queue: Queue, output_queue: Queue):
    
    while True:
        item = input_queue.get()

        if item is None:
            break

        num, id = item

        try:
            result = process_number(num)
            output_queue.put((result, id))
        except Exception as e:
            print(f"Не получилось посчитать число {num} по причине {e}")

def multiprocessing_queue_processing(n: int):
    input_queue = Queue()
    output_queue = Queue()

    processes = []

    processes_count = os.cpu_count() or 1

    numbers = generate_data(n)
    
    for _ in range(processes_count):
        p = Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for i, num in enumerate(numbers):
        input_queue.put((num, i))

    for _ in range(processes_count):
        input_queue.put(None)

    results = [None] * n
    
    for _ in range(n):
        result, id = output_queue.get()
        results[id] = result

    for p in processes:
        p.join()

    return results

if __name__ == "__main__":
    
    processing_size = 1_000_000

    start = time.time()

    multiprocessing_pool_processing(processing_size)

    print(f"Pool = {time.time() - start:.4f} сек.")

    start = time.time()

    concurrent_processing(processing_size)

    print(f"concurrent = {time.time() - start:.4f} сек.")

    start = time.time()

    multiprocessing_queue_processing(processing_size)

    print(f"queue = {time.time() - start:.4f} сек.")
