import threading
import logging
from kettle import ElectricKettle

kettle = ElectricKettle()

# создаем логгер и задаем уровень логирования
logger = logging.getLogger('ElectricKettle')
logger.setLevel(logging.INFO)

# создаем обработчик, который будет выводить сообщения в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# создаем обработчик, который будет записывать сообщения в файл
file_handler = logging.FileHandler('electric_kettle.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# создаем форматтер для сообщений
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# привязываем обработчики к логгеру и форматтеру
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

addd = True

while addd:
    print('Текущее состояние чайника:', kettle.state)

    action = input('Выберите действие\n1 - налить воду\n'
                   '2 - включить чайник\n'
                   '3 - остановить кипение\n'
                   '4 - вылить воду\n'
                   '5 - выключить чайник\n'
                   '6 - показать текущую температуру\n'
                   'Ввод:\n')
    if action == '4':
        kettle.temperature = 20

    if action == '1':
        volume = float(input('Введите количество воды (от 0 до 1.0 л): '))
        if volume < 0 or volume > 1.0:
            print('Ошибка: Некорректный объем воды')
        else:
            try:
                kettle.fill(volume)
                print(f'Воды в чайнике: {kettle.volume}л.')
                logger.info(f"Действие '{action}' было выполнено")
            except ValueError as e:
                print(f'Ошибка: {e}')
                logger.error(f"Ошибка: {e}")

    elif action == '2':
        try:
            kettle.turn_on()
            thr = threading.Thread(target=kettle.boil)
            thr.start()
            logger.info(f"Действие '{action}' было выполнено")
        except ValueError as e:
            print(f'Ошибка: {e}')
            logger.error(f"Ошибка: {e}")

    elif action == '3':
        kettle.stopped()
        logger.info(f"Действие '{action}' было выполнено")

    elif action == '4':
        try:
            kettle.pour()
            print(f'Воды в чайнике: {kettle.volume}л.')
            logger.info(f"Действие '{action}' было выполнено")
        except ValueError as e:
            print(f'Ошибка: {e}')
            logger.error(f"Ошибка: {e}")

    elif action == '5':
        kettle.turn_off()
        logger.info(f"Действие '{action}' было выполнено")

    elif action == '6':
        print(f'Текущая температура: {kettle.temperature} градусов')
        logger.info(f"Действие '{action}' было выполнено")

    else:
        print("Неверная команда")
        logger.error("Неверная команда")