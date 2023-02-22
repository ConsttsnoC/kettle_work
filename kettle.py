import logging
from transitions import Machine
import time
import configparser
import requests


class ElectricKettle:
    """
     Класс, представляющий электрический чайник.

     Атрибуты:
     -----------
     volume : float
         Объем чайника в литрах.
     temperature : int
         Текущая температура воды в чайнике в градусах Цельсия.
     is_on : bool
         Флаг, указывающий на состояние чайника - включен или выключен.

     Методы:
     -------
     turn_on()
         Включает чайник.
     turn_off()
         Выключает чайник.
     set_temperature(temp: int)
         Устанавливает температуру воды в чайнике.
     boil()
         Запускает процесс кипячения воды.
     """

    def __init__(self):
        """
               Конструктор класса ElectricKettle.

               Параметры:
               ----------
               volume : float
                   Объем чайника в литрах.
               temperature : int, optional
                   Начальная температура воды в чайнике в градусах Цельсия (по умолчанию 20).
               """
        # Создаем объект парсера
        parser = configparser.ConfigParser()
        # Считываем файл config.ini
        parser.read('config.ini')
        # Получаем значение переменной max_volume из секции [kettle] в файле
        # config.ini
        max_volume = float(parser.get('kettle', 'max_volume'))
        temperature = int(parser.get('kettle', 'temperature'))
        self.max_volume = max_volume  # максимальный объём воды
        self.volume = 0  # объём воды, который на данный момент находится в чайнике
        self.power_on = False  # атрибут, который указывает на состояние работы электрочайника
        # атрибут, который указывает на то, кипит ли вода в чайнике в данный
        # момент.
        self.boiling = False
        self.temperature = temperature
        self.max_temperature = parser.getint('kettle', 'max_temperature')
        self.states = [
            'Выключен',
            'Включен',
            'Кипение',
            'Остановлен',
            'Пустой',
            'Наполненный',
            'Полный']
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='Пустой')
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
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # привязываем обработчики к логгеру и форматтеру
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def fill(self, volume):
        if self.volume + volume > self.max_volume:  # проверка на перелив
            # аварийное завершение программы
            raise ValueError('Слишком много воды')
        self.volume += volume  # добавление объема воды к текущему объему
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='Наполненный')
        response = requests.get(
            'http://127.0.0.1:5000/new_message/Наполненный')
        if self.volume == self.max_volume:
            self.machine = Machine(
                model=self,
                states=states,
                transitions=transitions,
                initial='Полный')
            response = requests.get('http://127.0.0.1:5000/new_message/Полный')

    def turn_on(self):
        """Включает чайник."""
        if self.volume == 0:  # проверка на наличие воды
            raise ValueError('Нет воды')  # аварийное завершение программы
        self.power_on = True  # если вода есть, то устанавливем кнопку включения в True

    def turn_off(self):
        """Выключает чайник."""
        self.power_on = False  # отключение питания чайника
        self.boiling = False  # вода перестала кипеть
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='Выключен')
        response = requests.get('http://127.0.0.1:5000/new_message/Выключен')
        print('Чайник выключен')

    def stopped(self):
        """
           Обрабатывает событие "остановка" и выполняет соответствующие действия:
               - отключает питание чайника;
               - прекращает кипение воды;
               - отправляет сообщение об изменении состояния чайника на сервер.
           """
        self.power_on = False  # отключение питания чайника
        self.boiling = False  # вода перестала кипеть
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='Остановлен')
        response = requests.get('http://127.0.0.1:5000/new_message/Остановлен')
        print('Чайник выключен')

    def boil(self):
        """Метод для кипячения воды в электрочайнике.

    Если в электрочайнике нет воды (self.volume == 0), генерируется ValueError.
    Если электрочайник выключен (self.power_on == False), инициализируется машина состояний self.machine,
    устанавливается начальное состояние 'Кипение' и устанавливается флаг self.power_on в True.
    Температура воды постепенно повышается в диапазоне от текущей температуры self.temperature
    до максимальной температуры self.max_temperature с шагом в 10 градусов Цельсия.
    В процессе кипячения текущая температура выводится на экран, а также происходит задержка в 1 секунду.
    Когда температура достигает 100 градусов Цельсия, происходит вызов HTTP-запроса по адресу
    'http://127.0.0.1:5000/new_message/Кипение'.
    Если в процессе кипячения электрочайник был выключен (self.power_on == False), операция прерывается.
    Когда вода закипит, вызывается метод self.stopped() для перевода электрочайника в состояние 'Остановлен'.
"""
        if self.volume == 0:
            raise ValueError('Нет воды')
        if not self.power_on:
            self.machine = Machine(
                model=self,
                states=states,
                transitions=transitions,
                initial='Кипение')
            self.power_on = True
        for i in range(int(self.temperature), self.max_temperature + 1, 10):
            if not self.power_on:
                break
            self.temperature = i
            print(f'Текущая температура: {self.temperature} градусов Цельсия')
            time.sleep(1)
            if self.temperature == 100:
                response = requests.get(
                    'http://127.0.0.1:5000/new_message/Кипение')
        else:
            print('Вода вскипела!')
            self.stopped()

    def pour(self):
        """Метод для сброса объема и инициализации состояний и переходов машины."""
        self.volume = 0
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='Пустой')
        response = requests.get('http://127.0.0.1:5000/new_message/Пустой')

    def get_temperature(self):
        """Функция возвращает текущую температуру чайника"""
        return self.temperature

    def load_config(self, config_file='config.ini'):
        """Функция загружает конфигурационный файл и извлекает настройки для чайника."""
        config = configparser.ConfigParser()
        config.read(config_file)
        self.max_volume = int(config['kettle']['max_volume'])


# список состояний электрочайника
states = [
    'Выключен',  # электрочайник выключен и не готов к использованию
    'Включен',  # электрочайник включен и готов к использованию
    'Кипение',  # вода в электрочайнике находится в процессе кипения
    'Остановлен',  # процесс кипения воды в электрочайнике остановлен
    'Пустой',  # электрочайник пустой и не содержит воды
    'Наполненный',  # в электрочайнике находится достаточное количество воды для приготовления напитка
    'Полный'  # электрочайник полностью заполнен водой и необходимо удалить излишки
]

'''
'trigger': это название метода класса ElectricKettle, который будет вызван для выполнения перехода.
'source': это текущее состояние, из которого будет выполнен переход.
'dest': это состояние, в которое будет выполнен переход.
'''
transitions = [
    # выключение электрочайника при наличии воды
    {'trigger': 'fill', 'source': 'Включен', 'dest': 'Выключен'},
    # включение электрочайника без воды
    {'trigger': 'fill', 'source': 'Выключен', 'dest': 'Включен'},
    # аварийное отключение при кипении воды
    {'trigger': 'fill', 'source': 'Кипение', 'dest': 'Выключен'},
    {'trigger': 'turn_on',
     'source': 'Кипение',
     'dest': 'Остановлен'},
    # остановка кипячения
    # выключение электрочайника с водой
    {'trigger': 'turn_off', 'source': 'Включен', 'dest': 'Остановлен'},
    # наполнение электрочайника водой
    {'trigger': 'turn_off', 'source': 'Пустой', 'dest': 'Наполненный'},
    {'trigger': 'turn_off', 'source': 'Пустой',
     'dest': 'Полный'},  # электрочайник полон
    # удаление излишков воды из электрочайника
    {'trigger': 'turn_off', 'source': 'Полный', 'dest': 'Пустой'},
    # использование воды из электрочайника
    {'trigger': 'turn_off', 'source': 'Наполненный', 'dest': 'Пустой'},
]
