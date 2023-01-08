import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_manager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Environment variables
load_dotenv()
database_uri = os.environ.get('DATABASE_URI')
secret_key = os.environ.get('SECRET_KEY')

# Initialize app and database
database = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = str(database_uri)
app.config['SECRET_KEY'] = str(secret_key)
database.init_app(app)

# Table classes for database
class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=False)
    date_created = database.Column(database.DateTime, server_default=database.func.current_timestamp(), nullable=False)

class Room(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    is_double = database.Column(database.Boolean, nullable=False)

class Reservation(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    customer_id = database.Column(database.ForeignKey(User.id), nullable=False)
    room_id = database.Column(database.ForeignKey(Room.id), nullable=False)
    amount_of_guests = database.Column(database.Integer, nullable=False)
    start_date = database.Column(database.Date, nullable=False)
    end_date = database.Column(database.Date, nullable=False)
    price = database.Column(database.Integer, nullable=False)
    is_paid = database.Column(database.Boolean, nullable=False)
    date_created = database.Column(database.DateTime, server_default=database.func.current_timestamp(), nullable=False)
    date_modified = database.Column(database.DateTime, server_onupdate=database.func.current_timestamp(), nullable=False)

with app.app_context():
    database.create_all()

# Forms
class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# App routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    name = None
    form = SignUpForm()
    # Validate form
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            user = User(name=form.name.data)
            database.session.add(user)
            database.session.commit()
        name = form.name.data
        form.name.data = ''
    return render_template('signup.html', name=name, form=form)

# Start app
app.run()