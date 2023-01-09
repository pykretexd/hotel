from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Log in')

class UpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Update account')

class ReservationForm(FlaskForm):
    amount_of_guests = StringField('Amount of guests', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[DataRequired()])
    end_date = DateField('End date', validators=[DataRequired()])
    submit = SubmitField('Continue')

class ConfirmForm(FlaskForm):
    pay = BooleanField('Would you like to pay now? Reservation will be removed if not paid within 10 days.')
    submit = SubmitField('Confirm')