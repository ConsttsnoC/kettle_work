import threading
import logging
from kettle import ElectricKettle

# Создаем экземпляр электрического чайника
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
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# привязываем обработчики к логгеру и форматтеру
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

Job = True

while Job:
    # выводим текущее состояние чайника
    print('Текущее состояние чайника:', kettle.state)
    # принимаем команду от пользователя
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
        # принимаем объем воды от пользователя
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
    # если команда - "включить чайник"
    elif action == '2':
        try:
            # включаем чайник и запускаем поток для кипячения воды
            kettle.turn_on()
            thr = threading.Thread(target=kettle.boil)
            thr.start()
            logger.info(f"Действие '{action}' было выполнено")
        except ValueError as e:
            print(f'Ошибка: {e}')
            logger.error(f"Ошибка: {e}")
    # если команда - "остановить кипение"
    elif action == '3':
        # останавливаем кипячение воды
        kettle.stopped()
        logger.info(f"Действие '{action}' было выполнено")
    # если команда - "вылить воду"
    elif action == '4':
        try:
            kettle.pour()
            print(f'Воды в чайнике: {kettle.volume}л.')
            logger.info(f"Действие '{action}' было выполнено")
        except ValueError as e:
            print(f'Ошибка: {e}')
            logger.error(f"Ошибка: {e}")
    # выключаем чайник
    elif action == '5':
        kettle.turn_off()
        logger.info(f"Действие '{action}' было выполнено")

    elif action == '6':
        # выводим текущую температуру чайника
        print(f'Текущая температура: {kettle.temperature} градусов')
        logger.info(f"Действие '{action}' было выполнено")

    else:
        print("Неверная команда")
        logger.error("Неверная команда")
