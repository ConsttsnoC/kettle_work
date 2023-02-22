from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Message {self.id}>'

@app.route('/new_message/<text>')
def new_message(text):
    message = Message(text=text)
    db.session.add(message)
    db.session.commit()
    return f'Added new message: {text}'

@app.route('/get_messages')
def get_messages():
    messages = Message.query.all()
    return f'All messages: {[message.text for message in messages]}'

if __name__ == "__main__":
    app.run(debug=True)


@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

with app.app_context():
    db.create_all()