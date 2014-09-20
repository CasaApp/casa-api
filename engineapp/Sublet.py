from google.appengine.ext import ndb
import json
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
        sublet_key = self.put()
        post_data = {"sublet_id": sublet_key.id(), "price": self.price, "address": self.address, "tags": self.tags}
        return json.dumps(post_data)

    def Delete(self):
        return "This is a delete"
