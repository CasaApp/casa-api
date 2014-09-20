from google.appengine.ext import ndb

class TokenEntity(ndb.Model):

    EXPIRE_TIME = 5184000
    user_id = ndb.IntegerProperty()
    creation_time = ndb.DateTimeProperty()
