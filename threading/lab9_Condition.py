import threading
import time
import queue
import random


class MTS:
    def __init__(self):
        self.dict_users = {}
        self.count_users = 0
        self.pricing = {
            'Интернет': random.randint(2, 10),
            'Звонки': random.randint(2, 10),
            'СМС': random.randint(2, 10)
        }

    def new_user(self):
        number = f'+7({str(random.randint(901, 999))}){str(random.randint(401, 699))}-{str(random.randint(1000, 9999))}'
        balance = 100
        self.count_users += 1
        self.dict_users[number] = balance
        return number

    def change_pricing(self):
        self.pricing['Интернет'] = random.randint(2, 10)
        self.pricing['Звонки'] = random.randint(2, 10)
        self.pricing['СМС'] = random.randint(2, 10)
        return self.pricing

    def add_balance(self, number, n):
        self.dict_users[number] += n

    def spend_balance(self, number, option, n):
        amount = (self.pricing[option] * n)
        self.dict_users[number] -= amount
        return amount

    def get_balance(self, number):
        return self.dict_users[number]

    def check_balance(self, number):
        return self.dict_users[number] >= 0


def _generate_user_experience(number):
    options = {'Пополнить': random.randint(1, 50),
               'Интернет': random.randint(1, 10),
               'СМС': random.randint(1, 10),
               'Звонки': random.randint(1, 10),
               'Пропуск': 1
               }
    choice = random.choice(['Пополнить', 'Интернет', 'СМС', 'Звонки', 'Пропуск'])
    return {'Номер': number, 'Опция': choice, 'Количество': options[choice]}


def _forced_add_balance(number):
    amount = random.randint(100, 200)
    return {'Номер': number, 'Опция': 'Пополнить', 'Количество': amount}


def consumer(cond):
    """
    Ждет определенного состояния для использования ресурсов
    """
    th_name = threading.current_thread().name
    print(f'В сети новый абонент с номером: {th_name}')
    while True:
        with cond:
            with lock:
                if th_name not in critical_balances:
                    user_experience = _generate_user_experience(th_name)
                else:
                    user_experience = _forced_add_balance(th_name)
                    critical_balances.discard(th_name)
            Q.put(user_experience)
            cond.wait()


def producer(cond):
    """
    Подготовка ресурса для использования потребителями
    """
    while True:
        th_name = threading.current_thread().name
        with cond:
            # time.sleep(0.5)
            while not Q.empty():
                try:
                    order = Q.get_nowait()
                    if order['Опция'] == 'Пополнить':
                        print(f"{th_name}: Абонент {order['Номер']} пополняет счет на {order['Количество']}")
                        Producer.add_balance(order['Номер'], int(order['Количество']))
                    elif order['Опция'] in ('Интернет', 'Звонки', 'СМС'):
                        if Producer.check_balance(order['Номер']):
                            amount = Producer.spend_balance(order['Номер'], order['Опция'], order['Количество'])
                            print(f"{th_name}: Абонент {order['Номер']} тратит {amount} на {order['Опция']}")
                        else:
                            critical_balances.add(order['Номер'])
                            print(f"{th_name}: У абонента {order['Номер']} не хватает средств на счете")
                    else:
                        print(f"{th_name}: Абонент {order['Номер']} бездействует")
                    if not Producer.check_balance(order['Номер']):
                        critical_balances.add(order['Номер'])
                        print(f"{th_name}: У абонента {order['Номер']} не осталось средств на счете")
                    print(f"{th_name}: Текущее состояние абонента {order['Номер']} = {Producer.get_balance(order['Номер'])}")

                    time.sleep(0.2)

                    # Смена показателей тарифа
                    if random.randint(1, 25) == 5:
                        pricing = Producer.change_pricing()
                        print(f"{th_name}: !!! Расценки тарифа изменились !!!")
                        print(f"Новые расценки: \nСМС: {pricing['СМС']} \nЗвонки:{pricing['Звонки']} "
                              f"\nИнтернет: {pricing['Интернет']}")

                except Exception as e:
                    print(e)

            cond.notify_all()


lock = threading.Lock()
condition = threading.Condition()
Producer = MTS()
Q = queue.Queue()
critical_balances = set()

if __name__ == '__main__':
    for i in range(random.randint(5, 10)):
        """
        Создание потоков-потребителей
        """
        tr = threading.Thread(name=Producer.new_user(),
                              target=consumer,
                              args=(condition,))
        tr.start()

    # создание потока потребителей производителя
    p = threading.Thread(name='MTS',
                         target=producer,
                         args=(condition,))

    p.start()
