from google.appengine.ext import ndb

class ImageEntity(ndb.Model):

    image = ndb.BlobProperty()

    def Save(self):
        image_key = self.put()
        return image_key.id()
