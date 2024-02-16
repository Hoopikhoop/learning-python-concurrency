import threading
from threading import Thread, Barrier, Lock
import time


def function():
    current_thread = threading.current_thread().name
    thread_number = int(current_thread[-1])

    # Чтение значений из первого файла
    with lock:
        with open("file1.txt", 'r', encoding='utf-8') as file:
            products = [[line.split()[0], *map(int, line.split()[1:])] for line in file.read().splitlines()]
    print(f"Поток {current_thread} прочитал file1.txt")

    # Чтение значений из второго файла
    with lock:
        with open("file2.txt", 'r', encoding='utf-8') as file:
            order = [[*[list(map(int, value.split(':'))) for value in line.split()]]
                     for line in file.read().splitlines()][thread_number-1]
    print(f"Поток {current_thread} прочитал file2.txt")

    # Считаем, сколько выйдет для трех продуктов
    arr = [0 for i in range(8)]
    for i in range(thread_number-1, len(products), 3):
        for j in range(1, len(products[i])):
            arr[j-1] += products[i][j]

    # Проверка условия и добавление значений в словарь file3_txt
    if all([order[i][0] <= arr[i] <= order[i][1] for i in range(len(arr))]):
        file3_txt[thread_number] = [products[value][0] for value in range(thread_number-1, len(products), 3)]

        dict_vitamins = {}
        for j in range(len(arr)):
            if j == 0:
                dict_vitamins['Количество в граммах'] = arr[j]
            else:
                dict_vitamins['Витамин ' + ('A', 'B', 'C', 'D', 'E', 'P', 'F')[j-1]] = arr[j]
        file3_txt[thread_number].append(dict_vitamins)
    else:
        file3_txt[thread_number] = f"Поток {thread_number} не смог составить индивидуальный заказ"

    # Получение числа из барьера
    wait_int = barrier.wait()
    # Один из потоков записывает в файл
    if wait_int == 1:
        with open('file3.txt', 'w', encoding='utf-8') as file:
            for number, txt in file3_txt.items():
                file.write(f"{number}: {txt}\n")
        print(f"Поток {threading.current_thread().name} записал ответ в файл file3.txt")


if __name__ == "__main__":
    CNT_THREADS = 3
    barrier = Barrier(CNT_THREADS + 1)
    lock = Lock()  # Lock - Мьютекс

    file3_txt = {}
    for k in range(CNT_THREADS):
        thread = Thread(target=function)
        thread.start()

    barrier.wait()

