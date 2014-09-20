from google.appengine.ext import ndb
import json
class SubletEntity(ndb.Model):

    
    address = ndb.StringProperty()
    price = ndb.FloatProperty()
    tags = ndb.StringProperty(repeated=True)
    location = ndb.GeoPtProperty()
    start_date = ndb.DateTimeProperty()
    end_date = ndb.DateTimeProperty()
    description = ndb.TextProperty()
    
    def Get(self, sublet_id):
        post_data = {"sublet_id": sublet_id,
                     "price": self.price,
                     "address": self.address,
                     "tags": self.tags,
                     "start_date": self.start_date.isoformat(),
                     "end_date": self.end_date.isoformat(),
                     "description": self.description
                     }
        return json.dumps(post_data)

    def Put(self):
        return "This is a put"

    def Post(self):
        sublet_key = self.put()
        return self.Get(sublet_key.id())
    
    @staticmethod
    def Delete(sublet_id):
        sublet_key = ndb.Key(SubletEntity, sublet_id)
        if sublet_key.get() is None:
            return json.dumps({"status": "failure"})
        sublet_key.delete()
        return json.dumps({"status": "success"})
