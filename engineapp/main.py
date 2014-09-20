from flask import Flask
from flask import request
from flask import redirect
from Sublet import SubletEntity
from google.appengine.ext import ndb
app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/api/sublet', methods=['GET', 'PUT', 'POST', 'DELETE'])
def api_sublet():
    if request.method == 'POST':
        json = request.get_json()
        sublet = SubletEntity()
        sublet.address = json.get("address")
        sublet.price = json.get("price")
        if not json.get("tags") is None:
            sublet.tags = json.get("tags")
        sublet.location = ndb.GeoPt(json.get("latitude"), json.get("longtitude"))
        return sublet.Post()
    elif request.method == 'GET':
        sublet = SubletEntity()
        return sublet.Get()
    elif request.method == 'PUT':
        return sublet.Put()
    elif request.method == 'DELETE':
        return sublet.Delete()

@app.route('/')
def test():
    return "Hello World!"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
