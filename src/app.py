from datetime import datetime, date
import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import AvailabilityForm, ConfirmForm, ReservationForm, SignUpForm, LoginForm, UpdateUserForm, UpdateReservationForm

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

def date_validator(start: str, end: str):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except:
        flash('Invalid date.')
        return Exception('Invalid date')
    if start_date > end_date or start_date < date.today() or end_date < date.today():
        flash('Invalid date')
        return Exception('Invalid date')
    return start_date, end_date

# Table classes for database
class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), unique=True, nullable=False)
    date_created = database.Column(database.DateTime, server_default=database.func.current_timestamp(), nullable=False)
    reservations = database.relationship('Reservation', backref='user')

class Room(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    is_double = database.Column(database.Boolean, nullable=False)
    max_guests = database.Column(database.Integer, nullable=False)
    reservations = database.relationship('Reservation', backref='room')

class Reservation(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey(User.id), nullable=False)
    room_id = database.Column(database.Integer, database.ForeignKey(Room.id), nullable=False)
    amount_of_guests = database.Column(database.Integer, nullable=False)
    start_date = database.Column(database.Date, nullable=False)
    end_date = database.Column(database.Date, nullable=False)
    price = database.Column(database.Integer, nullable=False)
    is_paid = database.Column(database.Boolean, nullable=False)
    date_created = database.Column(database.DateTime, server_default=database.func.current_timestamp(), nullable=False)
    date_modified = database.Column(database.DateTime, server_default=database.func.current_timestamp(), server_onupdate=database.func.current_timestamp(), nullable=False)

with app.app_context():
    database.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def date_validator(start: str, end: str):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except:
        flash('Invalid date.')
        return Exception('Invalid date')
    if start_date > end_date or start_date < date.today() or end_date < date.today():
        flash('Invalid date')
        return Exception('Invalid date')
    return start_date, end_date

# App routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = AvailabilityForm()
    rooms = Room.query.all()
    if request.method == 'POST':
        try:
            start_date, end_date = date_validator(request.form['start_date'], request.form['end_date'])
        except:
            return render_template('index.html', form=form, rooms=rooms)
        filtered_rooms = []
        for room in rooms:
            if int(request.form['amount_of_guests']) <= room.max_guests:
                reservations = Reservation.query.filter_by(room_id=room.id).all()
                if reservations:
                    for reservation in reservations:
                        if not reservation.start_date <= start_date <= reservation.end_date or not reservation.start_date <= end_date <= reservation.end_date:
                            filtered_rooms.append(room)
                else:
                    filtered_rooms.append(room)
        return render_template('index.html', form=form, rooms=filtered_rooms)
    return render_template('index.html', form=form, rooms=rooms)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    name = None
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            user = User(name=form.name.data)
            database.session.add(user)
            database.session.commit()
            login_user(user)
            flash('Account successfully registered!')
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
    reservations = Reservation.query.all()
    form = UpdateUserForm()
    id = current_user.id
    user_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.name = request.form['name']
        try:
            database.session.commit()
            flash('Account successfully updated.')
            return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update, reservations=reservations)
        except:
            flash('Something went wrong, try again.')
            return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update, reservations=reservations)
    else:
        render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update, reservations=reservations)
    return render_template('dashboard.html', form=form, id=id, user_to_update=user_to_update, reservations=reservations)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/booking/<int:id>', methods=['GET', 'POST'])
@login_required
def booking(id):
    room = Room.query.get_or_404(id)
    form = ReservationForm()
    occupied_dates = []
    dates_booked = Reservation.query.filter_by(room_id=id).all()
    for occupied_date in dates_booked:
        occupied_dates.append({'start': occupied_date.start_date, 'end': occupied_date.end_date})
    if request.method == 'POST':
        amount_of_guests = int(request.form['amount_of_guests'])
        if amount_of_guests > room.max_guests:
            flash('Too many guests, please select another room or try again.')
            return render_template('booking.html', form=form, room=room, occupied_dates=occupied_dates)
        try:
            start_date, end_date = date_validator(request.form['start_date'], request.form['end_date'])
        except:
            return render_template('booking.html', form=form, room=room, occupied_dates=occupied_dates)
        for occupied_date in occupied_dates:
            if occupied_date['start'] <= start_date <= occupied_date['end'] or occupied_date['start'] <= end_date <= occupied_date['end'] or occupied_date['start'] >= start_date and end_date >= occupied_date['end']:
                flash('Date is unavailable, enter a new date.')
                return render_template('booking.html', form=form, room=room, occupied_dates=occupied_dates)
        delta = end_date - start_date
        session['price'] = amount_of_guests * 100 * delta.days
        return redirect(url_for('confirm', purpose='create', user_id=current_user.id, room_id=id, amount_of_guests=amount_of_guests, start_date=start_date, end_date=end_date))
    return render_template('booking.html', form=form, room=room, occupied_dates=occupied_dates)

@app.route('/booking/update_reservation/<int:id>', methods=['GET', 'POST'])
@login_required
def update_reservation(id):
    form = UpdateReservationForm()
    reservation = Reservation.query.get_or_404(id)
    if reservation is None:
        flash('An error occured, please try again.')
        return redirect(url_for('dashboard'))
    occupied_dates = []
    dates_booked = Reservation.query.filter_by(room_id=reservation.room_id).all()
    for occupied_date in dates_booked:
        if occupied_date.id == reservation.id:
            continue
        occupied_dates.append({'start': occupied_date.start_date, 'end': occupied_date.end_date})

    form.room_id.data = int(reservation.room_id)
    form.amount_of_guests.data = int(reservation.amount_of_guests)
    form.start_date.data = reservation.start_date
    form.end_date.data = reservation.end_date

    if form.validate_on_submit():
        room = Room.query.get_or_404(form.room_id.data)
        if room:
            if room.max_guests < form.amount_of_guests.data:
                flash('You have entered too many guests for the specified room.')
                return render_template('update_reservation.html', id=id, form=form, occupied_dates=occupied_dates)
            try:
                start_date, end_date = date_validator(request.form['start_date'], request.form['end_date'])
            except:
                return redirect(url_for('dashboard'))
            for occupied_date in occupied_dates:
                if occupied_date['start'] <= start_date <= occupied_date['end'] or occupied_date['start'] <= end_date <= occupied_date['end'] or occupied_date['start'] >= start_date and end_date >= occupied_date['end']:
                    flash('Date is unavailable, enter a new date.')
                    return render_template('update_reservation.html', id=id, form=form, occupied_dates=occupied_dates)
            delta = end_date - start_date
            new_price = form.amount_of_guests.data * 100 * delta.days
            
            session['reservation_id'] = reservation.id
            session['room_id'] = form.room_id.data
            session['amount_of_guests'] = form.amount_of_guests.data
            session['start_date'] = start_date
            session['end_date'] = end_date
            session['new_price'] = new_price
            return redirect(url_for('confirm', purpose='update'))
        else:
            flash('Room number is invalid.')
            return render_template('update_reservation.html', id=id, form=form, occupied_dates=occupied_dates)
    return render_template('update_reservation.html', id=id, form=form, occupied_dates=occupied_dates)

@app.route('/booking/pay/<int:id>', methods=['GET', 'POST'])
@login_required
def pay(id):
    form = ConfirmForm()
    reservation = Reservation.query.get_or_404(id)
    if reservation.is_paid == 1:
        flash('Reservation has already been paid for.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        reservation.is_paid = 1
        database.session.commit()
        flash('Transaction successful.')
        return redirect(url_for('dashboard'))
    return render_template('pay.html', form=form, reservation=reservation)

@app.route('/booking/delete/<int:id>')
@login_required
def delete_reservation(id):
    reservation_to_delete = Reservation.query.get_or_404(id)
    user_id = current_user.id
    if user_id == reservation_to_delete.user_id:
        try:
            database.session.delete(reservation_to_delete)
            database.session.commit()
            flash('Reservation has been cancelled.')
            return redirect(url_for('dashboard'))
        except:
            flash('An error occured, please try again.')
            return redirect(url_for('dashboard'))
    else:
        flash('You cannot cancel this reservation.')
        return redirect(url_for('dashboard'))

@app.route('/booking/confirm/<purpose>', methods=['GET', 'POST'])
@login_required
def confirm(purpose):
    form = ConfirmForm()
    if purpose == 'create':
        user = User.query.get_or_404(request.args.get('user_id'))
        room = Room.query.get_or_404(request.args.get('room_id'))
        amount_of_guests = request.args.get('amount_of_guests')
        try:
            start_date, end_date = date_validator(request.form['start_date'], request.form['end_date'])
        except:
            return redirect(url_for('dashboard'))
        price = session.get('price', None)
        if form.pay.data:
            is_paid = 1
        else:
            is_paid = 0
        if request.method == 'POST':
            try:
                reservation = Reservation(user_id=user.id, room_id=room.id, amount_of_guests=amount_of_guests, start_date=start_date, end_date=end_date, price=price, is_paid=is_paid)
                database.session.add(reservation)
                database.session.commit()
            except:
                flash('Something went wrong, try again.')
                return redirect(url_for('dashboard'))
            flash(f'Room {room.id} has successfully been booked.')
            return redirect(url_for('dashboard'))
    elif purpose == 'update':
        reservation = Reservation.query.get_or_404(int(session.get('reservation_id')))
        room_id = session.get('room_id')
        amount_of_guests = session.get('amount_of_guests')
        start_date = datetime.strptime(session.get('start_date'), '%Y-%m-%d').date() 
        end_date = datetime.strptime(session.get('end_date'), '%Y-%m-%d').date()
        new_price = session.get('new_price', None)
        try:
            reservation.room_id = room_id
            reservation.amount_of_guests = amount_of_guests
            reservation.start_date = start_date
            reservation.end_date = end_date
            reservation.price = new_price
            database.session.commit()
            flash('Reservation successfully updated.')
            return redirect(url_for('dashboard'))
        except:
            flash('Something went wrong, please try again.')
            return redirect(url_for('dashboard'))
    return render_template('confirm.html', form=form, price=price)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if id == current_user.id:
        user = User.query.get_or_404(id)
        user_reservation = Reservation.query.filter_by(user_id=user.id).first()
        if user_reservation:
            flash('You have active reservations. Please cancel all of them before deleting your account.')
            return redirect(url_for('dashboard'))
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
