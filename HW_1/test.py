import time

def sleep_generator(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        yield

def fetch_data(task_name, delay):
    print(f"{task_name}: Начало загрузки данных")
    yield from sleep_generator(delay)  # Симулируем задержку
    print(f"{task_name}: Данные загружены после {delay} секунд")

def run_generators(generators):
    tasks = list(generators)
    while tasks:
        for task in tasks.copy():
            try:
                next(task)
            except StopIteration:
                tasks.remove(task)

run_generators([
    fetch_data("Задача 1", 4),
    fetch_data("Задача 2", 2)
])