from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, BooleanField, IntegerField
from wtforms.validators import DataRequired

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Log in')

class UpdateUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Update account')

class ReservationForm(FlaskForm):
    amount_of_guests = IntegerField('Amount of guests', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[DataRequired()])
    end_date = DateField('End date', validators=[DataRequired()])
    submit = SubmitField('Continue')

class ConfirmForm(FlaskForm):
    pay = BooleanField('Would you like to pay now? Reservation will be removed if not paid within 10 days.')
    submit = SubmitField('Confirm')

class UpdateReservationForm(FlaskForm):
    room_id = IntegerField('Room number', validators=[DataRequired()])
    amount_of_guests = IntegerField('Amount of guests', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[DataRequired()])
    end_date = DateField('End date', validators=[DataRequired()])
    submit = SubmitField('Continue')

class AvailabilityForm(FlaskForm):
    amount_of_guests = IntegerField('Amount of guests')
    start_date = DateField('From')
    end_date = DateField('To')
    submit = SubmitField('Check for available rooms')