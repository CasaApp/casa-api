from google.appengine.ext import ndb
from werkzeug.security import generate_password_hash, check_password_hash
from Token import TokenEntity
import datetime
class UserEntity(ndb.Model):
    name = ndb.StringProperty()
    pw_hash = ndb.StringProperty()
    email = ndb.StringProperty()
    bookmarks = ndb.IntegerProperty(repeated=True)

    def ParseJson(self, text):
        self.name = text.get("name")
        self.pw_hash = generate_password_hash(text.get("password"))
        self.email = text.get("email")

    def Login(self):
        token = TokenEntity(user_id = self.key.id(),
                            creation_time = datetime.datetime.now())
        token_key = token.put()
        return {"token": token_key.urlsafe(),"expires_in": token.EXPIRE_TIME}
    
    def Get(self):
        post_data = {"name": self.name,
                     "email": self.email,
                     "user_id": self.key.id()}
        return post_data, self.Login()

    def Post(self, text):
        self.ParseJson(text)
        user_key = self.put()
        return self.Get()
