from google.appengine.ext import ndb
import json
import time
from datetime import datetime
from Image import ImageEntity

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
    rooms_available = ndb.IntegerProperty()
    rooms_total = ndb.IntegerProperty()
    image_ids = ndb.IntegerProperty(repeated=True)
    owner_id = ndb.IntegerProperty()
    
    def Get(self):
        post_data = {"sublet_id": self.key.id(),
                     "price": self.price,
                     "address": self.address,
                     "tags": self.tags,
                     "start_date": self.start_date.isoformat(),
                     "end_date": self.end_date.isoformat(),
                     "description": self.description,
                     "city": self.city,
                     "rooms_available": self.rooms_available,
                     "rooms_total": self.rooms_total,
                     "image_ids": self.image_ids,
		     "latitude": self.location.lat,
		     "longitude": self.location.lon,
                     "owner_id": self.owner_id
                     }
        return post_data
    
    def Put(self, json_text):
        return self.Post(json_text)

    def Post(self, json_text, owner_id):
        self.ParseJson(json_text)
        self.owner_id = owner_id
        self.put()
        return self.Get()
    
    def Delete(self):
        self.key.delete()
        return {"status": "success"}

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
        self.rooms_available = text.get("rooms_available")
        self.rooms_total = text.get("rooms_total")

    def AddImage(self, blob):
        image = ImageEntity()
        image.image = blob
        self.image_ids.append(image.Save())
        self.put()
        return self.Get()

    def RemoveImage(self, image_id):
        if image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.put()
            image = ImageEntity.get_by_id(image_id)
            image.key.delete()
        
        
        
