from flask import (Flask, g, render_template, redirect, flash, url_for,
send_from_directory)
from flask.ext.login import (LoginManager, login_user, logout_user,
login_required, current_user)
from flask.ext.bcrypt import check_password_hash
from werkzeug import secure_filename
from os import listdir, makedirs, remove
from os.path import isfile, join
import shutil
import models
import forms

DEBUG = True

app = Flask(__name__)
app.secret_key = 'sgsrgsfg@:&g%^46&&hww!$$fwrr'	


# login manager from flask-login
# handles user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# loads the user based on the user_id
# stored in the current session
@login_manager.user_loader
def load_user(user_id):
	try:
		return models.User.get(models.User.id == user_id)
	except models.DoesNotExist:
		return None


# called before any request
@app.before_request
def before_request():
	# connect to db before each request
	g.db = models.DATABASE
	g.db.connect()


# called after any request
@app.after_request
def after_request(response):
	# close db connection after request
	g.db.close()
	return response


# registration view, handles the displaying of the
# registration template, and the registering of users
@app.route('/register', methods=['GET', 'POST'])
def register():
	# sets the form as the registration form
	# imported from the forms module
	form = forms.RegistrationForm()
	# if the form is validated register 
	# the user with those credentials
	if form.validate_on_submit():
		flash('you have been registered! Please log in', 'success')
		# creating the user model
		models.User.create_user(
			username=form.username.data,
			email=form.email.data,
			password=form.password.data
		)

		# create user directory
		makedirs('uploads/{}'.format(form.username.data))

		return redirect(url_for('login'))
	# render the register template and pass in the form
	return render_template('register.html', form=form)


# login view, handles the logging in of a 
# user displays the login template
@app.route('/', methods=['GET', 'POST'])
def login():
	# sets the form as the login form 
	# imported from the forms module
	form = forms.LoginForm()
	# if the form validates log the user in
	if form.validate_on_submit():
		# try and find the user using the username in the form
		try:
			user = models.User.get(models.User.username == form.username.data)
		# if they do not exist inform them
		except models.DoesNotExist:
			flash('Your email or password does not exist', 'error')
		else:
			# if the password in the form is equal to the users
			# actual password then log them in
			# using the flask-bcrypt function to check the password
			# stored as a salted hash
			if check_password_hash(user.password, form.password.data):
				login_user(user)
				return redirect(url_for('index'))
			else:				
				flash('Your email or password does not exist', 'error')
	# render the login template and pass in the form
	return render_template('login.html', form=form)


# logout view, logs the user out 
# and redirects to the index page
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))


# index view, home page
# loads all users directories
@app.route('/home', methods=('GET', 'POST'))
@login_required
def index():
	# user base directory path
	userDir = 'uploads/{}'.format(current_user.username)
	# create a list of users directories
	dirs = [f for f in listdir(userDir) if not isfile(join(userDir, f))]
	# render template and pass over list of directories
	return render_template('index.html', dirs=dirs)


# allows user to switch between directories
# loads directory contents and handles file uploads
# to particular directory
@app.route('/directory/<path:dirname>', methods=['GET', 'POST'])
@login_required
def changeDir(dirname):
	# uplaod form object
	form = forms.UploadForm()
	# user base directory path
	userDir = 'uploads/{}'.format(current_user.username)
	# if the form is submitted then validate it
	if form.validate_on_submit():
		# create secure filename for uploaded file
		filename = secure_filename(form.upload.data.filename)
		# check if filename exists
		# flash a corresponding message to user
		if filename in listdir('{}/{}'.format(userDir, dirname)):
			flash('filename exists', 'error')
		else:
			# if file name does not exits then save the file to directory
			form.upload.data.save('{}/{}/{}'.format(userDir, dirname, filename))
			flash('file uploaded', 'success')
	else:
		# if no form is submitted then set file to none to 
		# allow the passing of this variable to the template
		filename = None	
	# create a list of filenames in this directory
	files = [f for f in listdir('{}/{}'.format(userDir, dirname)) 
			if isfile(join('{}/{}'.format(userDir, dirname), f))]
	# render template and pass over variables
	return render_template('directory.html', 
		files=files, form=form, filename=filename, dirname=dirname)


# creates a sub directory in users base directory
@app.route('/makedir/<path:dirname>')
@login_required
def createDir(dirname):
	# user base directory
	userDir = 'uploads/{}'.format(current_user.username)
	# make new sub directory in base directory
	makedirs('{}/{}'.format(userDir, secure_filename(dirname)))
	return redirect(url_for('index'))


# deletes sub directory and its contents
@app.route('/deletedir/<path:dirname>')
@login_required
def deleteDir(dirname):
	# sub directroy path
	dir = 'uploads/{}/{}'.format(current_user.username, dirname)
	# delete directory and contents
	shutil.rmtree(dir, ignore_errors=True)
	# flash message to user
	flash('folder was deleted', 'success')
	return redirect(url_for('index'))


# delete specific file in sub directory
@app.route('/deletefile/<path:dirname>/<path:filename>')
@login_required
def deleteFile(dirname, filename):
	# remove file at path
	remove('uploads/{}/{}/{}'.format(current_user.username, dirname, filename))
	# user message
	flash('file was deleted', 'success')
	# redirect back to current sub directory
	return redirect(url_for('changeDir', dirname=dirname))


# download specified file
@app.route('/download/<path:dirname>/<path:filename>')
@login_required
def download(dirname, filename):
	# directory where file exists
	dir = 'uploads/{}/{}'.format(current_user.username, dirname)
	# send the file from the directory!
	return send_from_directory(dir, filename, as_attachment=True)



if __name__ == '__main__':
	# initialize the database models/tables
	models.initialize()
	app.run(debug=DEBUG)
