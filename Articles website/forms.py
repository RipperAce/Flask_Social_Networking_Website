from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(2,25)])
	email = StringField('Email Id', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(8, 20)])
	confirmed_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	city = StringField('City', validators=[DataRequired(), Length(2,25)])
	country = StringField('Country', validators=[DataRequired(), Length(2,25)])
	birthdate = DateField('BirthDate', validators=[DataRequired()])
	submit = SubmitField('Register')

class LoginForm(FlaskForm):
	email = StringField('Email ID', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired(), Length(10,100)])
	content = CKEditorField('Content', validators=[DataRequired()])
	submit = SubmitField('Post')

class SearchBar(FlaskForm):
	search = StringField('Search Here', validators=[DataRequired()])
	submit = SubmitField('Search')

class UpdateAccount(FlaskForm):
	username = StringField('Email ID', validators=[DataRequired(), Length(2,25)])
	email = StringField('Email Id', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	city = StringField('City', validators=[DataRequired(), Length(2,25)])
	country = StringField('Country', validators=[DataRequired(), Length(2,25)])
	submit = SubmitField('Update')