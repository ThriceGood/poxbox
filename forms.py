from flask_wtf.file import FileField, FileRequired
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
								Email, Length, EqualTo)
from models import User


# name exists validator, checks if a username already exists
def name_exists(form, field):
	if User.select().where(User.username == field.data).exists():
		raise ValidationError('User with that name already exists')


# email exists validator, checks if a email already exists
def email_exists(form, field):
	if User.select().where(User.email == field.data).exists():
		raise ValidationError('User with that email already exists')


# the registration form, inherits for flask_wtf Form
class RegistrationForm(Form):
	# username field
	username = StringField(
		'Username',
		# validation rules
		# must not be empty
		# uppercase letters, lowercase letters, 0-9 and underscores
		# must not already exist
		validators = [
			DataRequired(),
			Regexp(
				r'^[a-zA-Z0-9_]+$',
				message='Username should be one word, leters, numbers \
				and underscores only'
			),
			name_exists
		]
	)
	# email field
	email = StringField(
		'Email',
		# validation rules
		# must not be empty
		# must be email format
		# must not already exist
		validators = [
			DataRequired(),
			Email(),
			email_exists
		]
	)
	# password field
	password = PasswordField(
		'Password',
		# validation rules
		# must not be empty
		# must at least 4 characters
		# must be equal to second password field
		validators = [
			DataRequired(),
			Length(min=4),
			EqualTo('password2', message='Passwords must match')
		]
	)
	# second password field for password confirmation
	password2 = PasswordField(
		'Confirm Password',
		# validation rules
		# must not be empty
		validators = [DataRequired()]
	)


# the login form
class LoginForm(Form):
	# user name field
	username = StringField(
		'Username',
		# validation rules
		# must not be empty
		validators = [DataRequired()]
	)
	# password field
	password = PasswordField(
		'Password',
		# validation rules
		# must not be empty
		validators = [DataRequired()]
	)


class UploadForm(Form):
    upload = FileField('file', validators=[
        FileRequired('file is required'),
    ])