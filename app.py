from flask import Flask, request, jsonfiy
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from flask_login import LoginManager, login_user
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = ''

login_manager = LoginManager()
app.secret_key = 'secretKey'

heroku = Heroku(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__= 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True, nullable=False)
    password = db.Column(db.String, nullable=False)
    entries = db.relationship('Journal', backref='author', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True
    
    def get_id(self):
        return self.email

    def __repr__(self):
        return "<User %r>" % self.name

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        email = request.get_json('email')
        password = request.get_json('password')
        registered_user = User.query.filter_by(email=email, password=password).first()
        login_user(registered_user)
        return jsonfiy('Logged_In')
        if registered_user is None:
            return jsonfiy('Not_Logged_In')
    return jsonfiy('something when wrong')  

@app.route('/register', methods=['POST'])
def register():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        name = post_data.get('name')
        email = post_data.get('email')
        password = post_data.get('password')
        reg = User(name, password, email)
        db.session.add(reg)
        db.session.commit()
        return jsonfiy('Created')
    return jsonfiy('something went wrong')

@app.route('/get-users', methods=['GET'])
def get_users():
    all_users = db.session.query(User.id, User.name, User.email, User.password).all()
    return jsonfiy(all_users)


class Journal(db.Model):
    __tablename__='journal'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gratitude1 = db.Column(db.String)
    gratitude2 = db.Column(db.String)
    gratitude3 = db.Column(db.String)
    today = db.Column(db.String(50))
    entry = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, date, gratitude1, gratitude2, gratitude3, today, entry):
        self.title = title
        self.date = date
        self.gratitude1 = gratitude1
        self.gratitude2 = gratitude2
        self.gratitude3 = gratitude3
        self.today = today
        self.entry = entry

    def __repr__(self):
        return '<Journal %r>' %(self.date)


if __name__ == '__main__':
    app.debug = True
    app.run()