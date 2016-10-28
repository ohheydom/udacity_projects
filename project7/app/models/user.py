from google.appengine.ext import ndb
from protorpc import messages


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    email_me = ndb.BooleanProperty(default=True)


class NewUserForm(messages.Message):
    username = messages.StringField(1, required=True)
    email = messages.StringField(2)
    email_me = messages.BooleanField(3, default=True)

