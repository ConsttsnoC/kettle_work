from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Message(db.Model):
    """
       Класс, представляющий модель для сообщений о выполненной работе.

       Attributes:
           id (int): уникальный идентификатор сообщения.
           work_done (str): описание выполненной работы.
           time_done (datetime): дата и время, когда работа была выполнена.

       """
    id = db.Column(
        db.Integer,
        primary_key=True)  # уникальный идентификатор сообщения
    # описание выполненной работы
    work_done = db.Column(db.String(200), nullable=False)
    # дата и время, когда работа была выполнена
    time_done = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # возвращаем строку вида <Message {id}>, где id - уникальный идентификатор
    # сообщения
    def __repr__(self):
        return f'<Message {self.id}>'
