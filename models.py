from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_done = db.Column(db.String(200), nullable=False)
    time_done = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<Message {self.id}>'

