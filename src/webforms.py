from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
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