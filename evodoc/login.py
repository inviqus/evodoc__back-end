import uuid
from evodoc.app import db
from evodoc.exception import DbException, ApiException
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from datetime import datetime, timedelta
from evodoc.entity import *

def login(username, password_plain):
	user = User.get_user_by_username_or_email(User, username)
	if user.activated == False:
		token = authenticateUser(user.id)
		raise ApiException(200, {"data": "User not activated", "token": token})
	if (user.confirm_password(password_plain)):
		return authenticateUser(user.id, None)

def createToken (userId) : #creates new token and adds it to the database
	t = str(userId).zfill(10) + str(uuid.uuid4())
	while (UserToken.query.filter_by(token=t).count() != 0) :
		t = str(userId).zfill(10) + str(uuid.uuid4())
	db.session.add(UserToken(user_id=userId,token=t))
	db.session.commit()
	return t

def authenticateUser (id, token=None): #returns active token
	if (token==None) :
		return createToken(id)
	#make sure the token is active
	for token in UserToken.query.filter(UserToken.user_id==id, UserToken.created +  timedelta(hours=24) > datetime.utcnow(), UserToken.update +  timedelta(hours=2) > datetime.utcnow()):
		token.update=datetime.utcnow()#if token is active update it
		t=token.token
		db.session.commit()

		return t
	#otherwise createToken(id)
	return createToken(id)

def authenticate(token):
	"""
	Test if token exist, if not returns None, if its out of date, returns new token, else return old one
		:param token: user token
	"""
	if token == None:
		return None
	userTokenEntity = UserToken.query.filter((UserToken.token == token) or ((UserToken.created + timedelta(hours=24)) > datetime.now()) or ((UserToken.update +  timedelta(hours=2)) > datetime.now())).first()
	if userTokenEntity == None:
		return None
	if userTokenEntity.user.active != 1:
		return None
	return userTokenEntity

def check_token_exists(token):
	return userToken.query.filter((UserToken.token == token)).first()
