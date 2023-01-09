import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import SignUpForm, LoginForm, UpdateForm

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# App routes
@app.route('/')
def index():
    return render_template('index.html')

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
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Account already exists.')
        name = form.name.data
        form.name.data = ''
    return render_template('signup.html', name=name, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Could not find account - Try again.')
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateForm()
    id = current_user.id
    user_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.name = request.form['name']
        try:
            database.session.commit()
            flash('Account successfully updated.')
            return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update)
        except:
            flash('Something went wrong, try again.')
            return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update)
    else:
        render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update)
    return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if id == current_user.id:
        user = User.query.get_or_404(id)
        try:
            database.session.delete(user)
            database.session.commit()
            flash('Your account has been successfully deleted.')
            return redirect(url_for('index'))
        except:
            flash('An error occured, please try again.')
    else:
        flash("You can't delete that user.")
        return redirect(url_for('dashboard'))

# Start app
app.run()