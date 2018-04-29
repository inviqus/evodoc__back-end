"""User: Contains all entities that are related to user
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, desc
from evodoc.app import db
import bcrypt
from evodoc.exception import DbException

###################################################################################
class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_type_id =Column(Integer, ForeignKey("user_type.id"))
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(128), nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow())
    update = Column(DateTime, default=datetime.datetime.utcnow())
    active = Column(Boolean)
    activated = Column(Boolean)
    tokens = db.relationship('UserToken', backref='user', lazy=False)

    def __init__(self, name=None, email=None, password=None, created=None, update=None, active=True, activated = False):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.created = created
        self.active = active
        self.activated = activated
        self.user_type_id = UserType.get_type_by_name("GUEST").id

    def __repr__(self):
        return "<User %r>" % (self.name)

    @classmethod
    def get_user_by_id(cls, userId, raiseFlag = True):
        user = User.query.filter_by(id=userId).first()
        if (user == None) & raiseFlag:
            raise DbException(404, "User not found.")
        return user

    @classmethod
    def get_user_by_name(cls, userName, raiseFlag = True):
        user = User.query.filter_by(name=userName).first()
        if (user == None) & raiseFlag:
            raise DbException(404, "User not found.")
        return user

    @classmethod
    def get_user_by_email(cls, userEmail, raiseFlag = True):
        user = User.query.filter_by(email=userEmail).first()
        if (user == None) & raiseFlag:
            raise DbException(404, "User not found.")
        return user

    @classmethod
    def get_user_by_username_or_email(cls, username, raiseFlag = True):
        user = cls.query.filter((User.email == username) | (User.name == username)).first()
        if (user == None)  & raiseFlag:
            raise DbException(404, "User not found.")
        return user

    @classmethod
    def get_user_all(cls, raiseFlag = True):
        user = cls.query.all()
        if (user == None) and raiseFlag:
            raise DbException(404, "No user found.")
        return user

    @classmethod
    def get_user_all_by_user_type_id(cls, userType, raiseFlag = True):
        user = User.query.filter_by(user_type_id=userType).all()
        if (user == None) & raiseFlag:
            raise DbException(404, "No user found.")
        return user

    @classmethod
    def update_user_type_by_id(cls, id, userType, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.user_type_id = userType
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def update_activation_by_id(cls, id, activated, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.activated = activated
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def update_user_email_by_id(cls, id, email, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.email = email
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def update_user_password_by_id(cls, id, password, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def update_user_name_by_id(cls, id, name, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.name = name
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def activate_user_by_id(cls, id):
        user = User.get_user_by_id(id)
        if (user == None):
            return False
        user.active = True
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def deactivate_user_by_id(cls, id, raiseFlag = True):
        user = User.get_user_by_id(id, raiseFlag)
        if (user == None):
            return False
        user.active = False
        user.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    def save_entity(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def check_unique(cls, username, email, raiseFlag = False):
        """
        Check if username and email are not presented in database (check unique)
            :param self:
            :param username:
            :param email:
            :param raiseFlag=False: if its true this function raise exception if email or username are already presented
        """

        userEmail = User.get_user_by_email(email, False)
        userName = User.get_user_by_name(username, False)

        if raiseFlag:
            if userEmail != None:
                raise DbException(400, "email")
            if userName != None:
                raise DbException(400, "username")
            return True
        else:
            if userEmail != None:
                return False
            if userName != None:
                return False
            return True

    def confirm_password(self, password_plain):
        if (bcrypt.checkpw(password_plain.encode("utf-8"), self.password.encode("utf-8"))):
            return True
        else:
            return False

    @classmethod
    def update_user_by_id_all(cls, name=None, email=None, password=None, created=None, update=None, active=None, activated = None, raiseFlag = True):
        usr = cls.get_user_by_id(id, raiseFlag)
        if (usr == None):
            return False
        changed = 0

        if (name!=None):
            usr.name = name
            changed = 1
        if (email!=None):
            usr.email = email
            changed = 1
        if (password!=None):
            usr.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).encode("utf-8")
            changed = 1
        if (created!=None):
            usr.created = created
            changed = 1
        if (active!=None):
            usr.active = active
            changed = 1
        if (activated!=None):
            usr.activated = activated
            changed = 1

        if ((changed == 1) and (update == None)):
            usr.update = datetime.datetime.utcnow
            db.session.commit()
        if (update  !=None):
            usr.update = update
            db.session.commit()
        return True

    @classmethod
    def update_user_by_id_all_list(cls, userList, raiseFlag = True):
        failedUpdatesList = []
        for i in userList:
            if (cls.update_user_by_id_all(name=i.name, email=i.email, password=i.password, created=i.created, update=i.update, active=i.active, activated=i.activated, raiseFlag=raiseFlag) == False):
                failedUpdatesList.append(i)
        return i

    @classmethod
    def update_user_by_id_from_array(cls, id, dataArray):
        userEntity = cls.get_user_by_id(id)
        # Name change
        if dataArray["name"] != None:
            userCheck = cls.get_user_by_name(dataArray["name"], False)
            if userCheck != None & userCheck.id != id:
                raise DbException(400, "username")
            userEntity.username = dataArray["name"]

        if dataArray["email"] != None:
            userCheck = cls.get_user_by_email(dataArray["email"], False)
            if userCheck != None & userCheck.id != id:
                raise DbException(400, "email")
            userEntity.username = dataArray["email"]

        if dataArray["password"] != None:
             userEntity.password = bcrypt.hashpw(dataArray["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        if dataArray["user_type_id"] != None:
            userType = UserType.get_type_by_id(UserType, dataArray["user_type_id"], False)
            if userType == None:
                raise DbException(400, "usertype")
            userEntity.user_type_id = dataArray["user_type_id"]

        db.session.commit()
        return userEntity

    def serialize(self):
        return {
            'id': self.id,
            'user_type_id': self.user_type_id,
            'name': self.name,
            'email': self.email,
            'created': self.created,
            'update': self.update,
            'active': self.active,
        }

    @classmethod
    def get_user_type_perm_from_user_id(cls, id, raiseFlag = True):
        usr = cls.get_user_by_id(id, raiseFlag)
        if (usr == None): return 0
        t = UserType.get_type_by_id(usr.user_type_id, raiseFlag)
        if (t == None): return 0
        return t.permission_flag

###################################################################################
class UserType(db.Model):
    __tablename__ = "user_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    permission_flag = Column(Integer)
    users = db.relationship('User', backref='user_type', lazy=True)

    def __init__(self, name=None, permission_flag=0):
        self.name = name
        self.permission_flag = permission_flag

    def __repr__(self):
        return "<UserType %r>" % (self.name)

    @classmethod
    def get_type_by_id(cls, typeId, raiseFlag = True):
        userType = cls.query.filter_by(id=typeId).first()
        if (userType == None) & raiseFlag:
            raise DbException(404, "UserType not found.")
        return userType

#    def get_type_by_name(self, typeName, raiseFlag = True):
#        userType = self.query.filter_by(name=typeName).first()
#        if (userType == None) & raiseFlag:
#            raise DbException(DbException, 404, "UserType not found.")
#        return userType

    @classmethod
    def get_type_by_name(cls, typeName, raiseFlag = True):
        userType = cls.query.filter_by(name=typeName).first()
        if (userType == None) & raiseFlag:
            raise DbException(404, "UserType not found.")
        return userType

    @classmethod
    def get_type_all(cls, raiseFlag = True):
        userType = cls.query.all()
        if (userType == None) & raiseFlag:
            raise DbException(404, "No userType found.")
        return userType

    @classmethod
    def update_type_name_by_id(cls, id, name, raiseFlag = True):
        userType = cls.get_type_by_id(User, id, raiseFlag)
        if (userType == None):
            return False
        userType.name = name
        db.session.commit()
        return True

    @classmethod
    def update_type_permisson_by_id(cls, id, permission, raiseFlag = True):
        userType = cls.get_type_by_id(User, id, raiseFlag)
        if (userType == None):
            return False
        userType.permission = permission
        db.session.commit()
        return True

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'permission_flag':self.permission_flag
        }

###################################################################################
class UserToken(db.Model):
    __tablename__ = "user_token"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    token = Column(String(47), unique=True)
    created = Column(DateTime, default=datetime.datetime.utcnow())
    update = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(self, user_id=None, token=None, created=None, update=None):
        self.user_id=user_id
        self.token=token
        self.created=created
        self.update=update

    def __repr__(self):
        return "<UserToken %r>" % (self.token)

    @classmethod
    def get_token_by_id(cls, tokenId, raiseFlag = True):
        userToken = cls.query.filter_by(id=tokenId).first()
        if (userToken == None) & raiseFlag:
            raise DbException(404, "UserToken not found.")
        return userToken

    @classmethod
    def get_token_by_user_id(cls, userId):         #returns newest token for user
        userToken = cls.query.filter_by(user_id=userId).order_by(desc(UserToken.created)).first()
        if (userToken == None):
            raise DbException(404, "UserToken not found.")
        return userToken

    @classmethod
    def get_token_all(cls, raiseFlag = True):
        userToken = cls.query.all()
        if (userToken == None) & raiseFlag:
            raise DbException(404, "No userToken found.")
        return userToken

    @classmethod
    def get_token_all_by_user_id(cls, userId, raiseFlag = True):
        userToken = cls.query.filter_by(user_id=userId).all()
        if (userToken == None) & raiseFlag:
            raise DbException(404, "No userToken found.")
        return userToken

    @classmethod
    def update_token_user_id_by_id(cls, id, userId, raiseFlag = True):
        userToken = cls.get_token_by_id(id, raiseFlag)
        if (userToken == None):
            return False
        userToken.userId = userId
        userToken.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def update_token_token_by_id(cls, id, token, raiseFlag = True):
        userToken = cls.get_token_by_id(id, raiseFlag)
        if (userToken == None):
            return False
        userToken.token = token
        userToken.update = datetime.datetime.utcnow()
        db.session.commit()
        return True

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'created': self.create,
            'update': self.update
        }

