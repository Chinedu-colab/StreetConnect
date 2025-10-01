from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10)])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class PostJobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    pay = StringField('Pay', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Plumbing', 'Plumbing'), ('Cleaning', 'Cleaning'), ('Repair', 'Repair'), ('Digital Skill','Digital skill'), ('Tech support', 'Tech support'), ('Farming','Farming'), ('Building & construction','Building & construction'), ('Teaching & Tutoring', 'Teaching & tutoring')], validators=[DataRequired()])
    poster_name = StringField('Your Name', validators=[DataRequired()])
    poster_contact = StringField('Your Contact', validators=[DataRequired()])
    submit = SubmitField('Post Job')