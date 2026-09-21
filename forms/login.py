from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):

    identifier = StringField(
        'Student Number or Email',
        validators=[
            DataRequired(message='Please enter your student number or email.'),
            Length(min=3, max=100, message='Identifier must be between 3 and 100 characters.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please enter your password.'),
            Length(min=6, max=128, message='Password must be between 6 and 128 characters.')
        ]
    )

    submit = SubmitField('Login')