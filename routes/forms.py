from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from forms import LoginForm  

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data
     
class LoginForm(FlaskForm):
    identifier = StringField('Email or Student Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    

    return render_template('login.html', form=form)

