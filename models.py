from peewee import *
from flask.ext.login import UserMixin
from flask.ext.bcrypt import generate_password_hash
import datetime

# using a MySQL database, peewee ORM and PyMySQL
DATABASE = MySQLDatabase("poxbox", host="localhost", user="flask", passwd="flask")

# the user model, inherits peewee's UserMixin and Model class
class User(UserMixin, Model):
	# credentials
	username = CharField(unique=True)
	email = CharField(unique=True)
	password = CharField(max_length=100)
	joined_at = DateTimeField(default=datetime.datetime.now)
	is_admin = BooleanField(default=False)

	class Meta:
		database = DATABASE
		order_by = ('-joined_at',)

	# creates the user model, saves to database
	@classmethod
	def create_user(cls, username, email, password, admin=False):
		try:
			cls.create(
				username=username,
				email=email,
				# using flask-bcrypt to hash the password
				password=generate_password_hash(password),
				is_admin=admin
			)
		# if user already exists raise ValueError
		except IntegrityError:
			raise ValueError("user already exits")


# initialize the database and create the tables
def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User], safe=True)
	DATABASE.close()
