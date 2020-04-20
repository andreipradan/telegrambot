import uuid

from bcrypt import gensalt, hashpw
from flask_login import UserMixin
from flask import session

from core import database
from flask_app import login_manager


@login_manager.user_loader
def user_loader(_id):
    return User.objects.get(_id=_id)


@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")
    if not username:
        return
    return User.objects.get(username=username)


class UserQuerySet:
    @classmethod
    def get(cls, **kwargs):
        data = database.get_collection("Users").find_one(kwargs)
        if data is not None:
            return User(**data)


class User(UserMixin):
    objects = UserQuerySet

    def __init__(self, username, email, password, _id=None):
        self.username = username
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    @classmethod
    def register(cls, username, email, password):
        user = cls.objects.get(email=email)
        if user is None:
            cls.create(username=username, email=email, password=password)
            session["email"] = email
            return True
        return False

    @classmethod
    def create(cls, **kwargs):
        kwargs["_id"] = uuid.uuid4().hex
        password = kwargs.get("password")
        if password:
            kwargs["password"] = hashpw(password.encode("utf8"), gensalt())
        return database.get_collection("Users").insert_one(kwargs)
