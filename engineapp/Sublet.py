from google.appengine.ext import ndb
import json
import time
from datetime import datetime

def get_date(date_string):
    return datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y-%m-%d")))

class SubletEntity(ndb.Model):

    address = ndb.StringProperty()
    price = ndb.FloatProperty()
    tags = ndb.StringProperty(repeated=True)
    location = ndb.GeoPtProperty()
    start_date = ndb.DateTimeProperty()
    end_date = ndb.DateTimeProperty()
    description = ndb.TextProperty()
    city = ndb.StringProperty()
    
    def Get(self):
        post_data = {"sublet_id": self.key.id(),
                     "price": self.price,
                     "address": self.address,
                     "tags": self.tags,
                     "start_date": self.start_date.isoformat(),
                     "end_date": self.end_date.isoformat(),
                     "description": self.description,
                     "city": self.city
                     }
        return post_data
    
    def Put(self, json_text):
        return self.Post(json_text)

    def Post(self, json_text):
        self.ParseJson(json_text)
        self.put()
        return self.Get()
    
    def Delete(self):
        self.key.delete()
        return json.dumps({"status": "success"})

    def ParseJson(self, text):
        self.address = text.get("address")
        self.price = text.get("price")
        if not text.get("tags") is None:
            self.tags = text.get("tags")
        self.location = ndb.GeoPt(text.get("latitude"), text.get("longitude"))
        self.start_date = get_date(text.get("start_date"))
        self.end_date = get_date(text.get("end_date"))
        self.description = text.get("description")
        self.city = text.get("city")
