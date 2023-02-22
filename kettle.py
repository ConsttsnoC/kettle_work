import logging
from transitions import Machine
import time
import configparser
import requests

class ElectricKettle:

    def __init__(self):
        # Создаем объект парсера
        parser = configparser.ConfigParser()
        # Считываем файл config.ini
        parser.read('config.ini')
        # Получаем значение переменной max_volume из секции [kettle] в файле config.ini
        max_volume = float(parser.get('kettle', 'max_volume'))
        temperature = int(parser.get('kettle', 'temperature'))
        self.max_volume = max_volume  # максимальный объём воды
        self.volume = 0  # объём воды, который на данный момент находится в чайнике
        self.power_on = False  # атрибут, который указывает на состояние работы электрочайника
        self.boiling = False  # атрибут, который указывает на то, кипит ли вода в чайнике в данный момент.
        self.temperature = temperature
        self.max_temperature = parser.getint('kettle', 'max_temperature')
        self.states = ['Выключен', 'Включен', 'Кипение', 'Остановлен', 'Пустой', 'Наполненный', 'Полный']
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Пустой')
        # создаем логгер и задаем уровень логирования
        self.logger = logging.getLogger('ElectricKettle')
        self.logger.setLevel(logging.INFO)

        # создаем обработчик, который будет выводить сообщения в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # создаем обработчик, который будет записывать сообщения в файл
        file_handler = logging.FileHandler('electric_kettle.log')
        file_handler.setLevel(logging.INFO)

        # создаем форматтер для сообщений
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # привязываем обработчики к логгеру и форматтеру
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)



    def fill(self, volume):
        if self.volume + volume > self.max_volume:  # проверка на перелив
            raise ValueError('Слишком много воды')  # аварийное завершение программы
        self.volume += volume  # добавление объема воды к текущему объему
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Наполненный')
        response = requests.get('http://127.0.0.1:5000/new_message/Наполненный')
        if self.volume == self.max_volume:
            self.machine = Machine(model=self, states=states, transitions=transitions, initial='Полный')
            response = requests.get('http://127.0.0.1:5000/new_message/Полный')


    def turn_on(self):
        if self.volume == 0:  # проверка на наличие воды
            raise ValueError('Нет воды')  # аварийное завершение программы
        self.power_on = True  # если вода есть, то устанавливем кнопку включения в True



    def turn_off(self):
        self.power_on = False  # отключение питания чайника
        self.boiling = False  # вода перестала кипеть
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Выключен')
        response = requests.get('http://127.0.0.1:5000/new_message/Выключен')
        print('Чайник выключен')

    def stopped(self):
        self.power_on = False  # отключение питания чайника
        self.boiling = False  # вода перестала кипеть
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Остановлен')
        response = requests.get('http://127.0.0.1:5000/new_message/Остановлен')
        print('Чайник выключен')

    def boil(self):
        if self.volume == 0:
            raise ValueError('Нет воды')
        if not self.power_on:
            self.machine = Machine(model=self, states=states, transitions=transitions, initial='Кипение')
            self.power_on = True
        for i in range(int(self.temperature), self.max_temperature + 1, 10):
            if not self.power_on:
                break
            self.temperature = i
            print(f'Текущая температура: {self.temperature} градусов Цельсия')
            time.sleep(1)
            if self.temperature == 100:
                response = requests.get('http://127.0.0.1:5000/new_message/Кипение')
        else:
            print('Вода вскипела!')
            self.stopped()

    def pour(self):
        self.volume = 0
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Пустой')
        response = requests.get('http://127.0.0.1:5000/new_message/Пустой')

    def get_temperature(self):
        return self.temperature

    def load_config(self, config_file='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.max_volume = int(config['kettle']['max_volume'])



# список состояний электрочайника
states = ['Выключен','Включен', 'Кипение', 'Остановлен','Пустой','Наполненный','Полный']

''' 
'trigger': это название метода класса ElectricKettle, который будет вызван для выполнения перехода.
'source': это текущее состояние, из которого будет выполнен переход.
'dest': это состояние, в которое будет выполнен переход.
'''
transitions = [
    {'trigger': 'fill', 'source': 'Включен', 'dest': 'Выключен'},
    {'trigger': 'fill', 'source': 'Выключен', 'dest': 'Включен'},
    {'trigger': 'fill', 'source': 'Кипение', 'dest': 'Выключен'},
    {'trigger': 'turn_on', 'source': 'Кипение', 'dest': 'Остановлен'},
    {'trigger': 'turn_off', 'source': 'Включен', 'dest': 'Остановлен'},
    {'trigger': 'turn_off', 'source': 'Пустой', 'dest': 'Наполненный'},
    {'trigger': 'turn_off', 'source': 'Пустой', 'dest': 'Полный'},
    {'trigger': 'turn_off', 'source': 'Полный', 'dest': 'Пустой'},
    {'trigger': 'turn_off', 'source': 'Наполненный', 'dest': 'Пустой'},
]
