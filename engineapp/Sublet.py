from google.appengine.ext import ndb

class SubletEntity(ndb.Model):

    address = ndb.StringProperty()
    price = ndb.FloatProperty()
    tags = ndb.StringProperty(repeated=True)
    location = ndb.GeoPtProperty()
        
    def Get(self):
        return "This is a get"

    def Put(self):
        return "This is a put"

    def Post(self):
        self.put()
        return "This is a post"

    def Delete(self):
        return "This is a delete"
