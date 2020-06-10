from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from flask_login import LoginManager, login_user, current_user
from datetime import datetime

app = Flask(__name__)
CORS(app)
login_manager = LoginManager()
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://qjtuqqhzategbu:daa14029f61b7eba56229fa1ca04405aaa89ad73829f9383e745ffdc9e075fe9@ec2-52-20-248-222.compute-1.amazonaws.com:5432/ddbqa9j3akfn66'

app.secret_key = 'newSecretKey'

heroku = Heroku(app)
db = SQLAlchemy(app)

login_manager.init_app(app)


@app.route("/")
def home():
    return"<h1>Hi from Flask</h1>"

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
        email = post_data.get('email')
        password = post_data.get('password')
        registered_user = User.query.filter_by(email=email, password=password).first()
        if registered_user is None:
            return jsonify('Not_Logged_In')
        login_user(registered_user)
        return jsonify('Logged_In')
    return jsonify('something when wrong')  

@app.route('/register', methods=['POST'])
def register():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        name = post_data.get('name')
        email = post_data.get('email')
        password = post_data.get('password')
        reg = User(name, email, password)
        db.session.add(reg)
        db.session.commit()
        return jsonify('Created')
    return jsonify('something went wrong')

# @app.route('/logged_in', methods=["GET"])
# def logged_in():
#     if current_user.is_authenticated:
#         return jsonify('Logged_In')
#     else:
#         return jsonify("Not_Logged_In")

@app.route("/logout")
def logout():
    logout_user()
    return jsonify("Logged_Out")

@app.route('/get-users', methods=['GET'])
def get_users():
    all_users = db.session.query(User.id, User.name, User.email, User.password).all()
    return jsonify(all_users)


class Journal(db.Model):
    __tablename__='journal'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gratitude1 = db.Column(db.String, nullable=True)
    gratitude2 = db.Column(db.String, nullable=True)
    gratitude3 = db.Column(db.String, nullable=True)
    today = db.Column(db.String(50), nullable=True)
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

@app.route('/new-entry', methods=['POST'])
def new_entry():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        title = post_data.get('title')
        date = post_data.get('date')
        gratitude1 = post_data.get('gratitude1')
        gratitude2 = post_data.get('gratitude2')
        gratitude3 = post_data.get('gratitude3')
        today = post_data.get('today')
        entry = post_data.get('entry')
        reg = Journal(title, date, gratitude1, gratitude2, gratitude3, today, entry)
        db.session.add(reg)
        db.session.commit()
        return('Data Posted')
    return jsonify('something went wrong')

@app.route('/entries', methods=["GET"])
def get_entries():
    all_entries = db.session.query(Journal.id, Journal.title, Journal.date, Journal.gratitude1, Journal.gratitude2, Journal.gratitude3, Journal.today, Journal.entry).all()
    return jsonify(all_entries)

@app.route('/entry/<id>', methods=['GET'])
def get_entry(id):
    one_entry = db.session.query(Journal.id, Journal.title, Journal.date, Journal.gratitude1, Journal.gratitude2, Journal.gratitude3, Journal.today, Journal.entry).filter(Journal.id == id).first()
    return jsonify(one_entry)

@app.route('/delete/<id>', methods=['DELETE'])
def delete_entry(id):
    record = db.session.query(Journal).get(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify('Deleted')

@app.route('/update-entry/<id>', methods=['PUT'])
def update_entry(id):
    if request.content_type == 'application/json':
        put_data = request.get_json()
        title = put_data.get('title')
        date = put_data.get('date')
        gratitude1 = put_data.get('gratitude1')
        gratitude2 = put_data.get('gratitude2')
        gratitude3 = put_data.get('gratitude3')
        today = put_data.get('today')
        entry = put_data.get('entry')
        record = db.session.query(Journal).get(id)
        record.title = title
        record.date = date
        record.gratitude1 = gratitude1
        record.gratitude2 = gratitude2
        record.gratitude3 = gratitude3
        record.today = today
        record.entry = entry
        db.session.commit()
        return jsonify('Updated')
    return jsonify('Failed Update')

if __name__ == '__main__':
    app.debug = True
    app.run()