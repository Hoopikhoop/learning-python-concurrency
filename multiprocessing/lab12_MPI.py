from multiprocessing import Process, Lock, Manager
import os


def function(lock, proc_number, dct):

    # Чтение значений из первого файла
    with lock:
        with open("file1.txt", 'r', encoding='utf-8') as file:
            products = [[line.split()[0], *map(int, line.split()[1:])] for line in file.read().splitlines()]
    print(f"Процесс {proc_number+1} прочитал file1.txt")

    # Чтение значений из второго файла
    with lock:
        with open("file2.txt", 'r', encoding='utf-8') as file:
            order = [[*[list(map(int, value.split(':'))) for value in line.split()]]
                     for line in file.read().splitlines()][proc_number]
    print(f"Процесс {proc_number+1} прочитал file2.txt")

    # Считаем, сколько выйдет для трех продуктов
    arr = [0 for i in range(8)]
    for i in range(proc_number, len(products), 3):
        for j in range(1, len(products[i])):
            arr[j - 1] += products[i][j]

    # Проверка условия и добавление значений в словарь file3_txt
    if all([order[i][0] <= arr[i] <= order[i][1] for i in range(len(arr))]):

        dict_vitamins = {}
        for j in range(len(arr)):
            if j == 0:
                dict_vitamins['Количество в граммах'] = arr[j]
            else:
                dict_vitamins['Витамин ' + ('A', 'B', 'C', 'D', 'E', 'P', 'F')[j - 1]] = arr[j]

        dct[proc_number] = [products[value][0] for value in range(proc_number, len(products), 3)] + [dict_vitamins]
    else:

        dct[proc_number] = f"Поток {proc_number+1} не смог составить индивидуальный заказ"


if __name__ == '__main__':

    with Manager() as manager:
        CNT_PROCESSES = 3
        l = Lock()
        file3_txt = manager.dict()

        procs = []
        for num in range(CNT_PROCESSES):
            procs.append(Process(target=function, daemon=True, args=(l, num, file3_txt)))
            procs[num].start()
            procs[num].join()

        with open('file3.txt', 'w', encoding='utf-8') as file:
            for number, txt in file3_txt.items():
                file.write(f"{number}: {txt}\n")
        print(f"Центральный процесс записал ответ в файл file3.txt")

