from flask import Flask
from flask import request
from flask import redirect
from Sublet import SubletEntity
from google.appengine.ext import ndb
import time
from datetime import datetime
app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def get_date(date_string):
    return datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y-%m-%d")))

@app.route('/api/sublet/<int:sublet_id>', methods=['GET', 'PUT', 'DELETE'])
def api_sublet_with_id(sublet_id):
    if request.method == 'GET':
        sublet = SubletEntity.get_by_id(sublet_id)
        if sublet is None:
            return "Not Found", 404
        return sublet.Get(sublet_id)
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        return SubletEntity.Delete(sublet_id)
    return "SUBLET ID"
           
@app.route('/api/sublet', methods=['GET', 'POST'])
def api_sublet():
    if request.method == 'POST':
        json = request.get_json()
        sublet = SubletEntity()
        sublet.address = json.get("address")
        sublet.price = json.get("price")
        if not json.get("tags") is None:
            sublet.tags = json.get("tags")
        sublet.location = ndb.GeoPt(json.get("latitude"), json.get("longitude"))
        sublet.start_date = get_date(json.get("start_date"))
        sublet.end_date = get_date(json.get("end_date"))
        sublet.description = json.get("description")
        return sublet.Post(), 201
    elif request.method == 'GET':
        sublet = SubletEntity()
        return sublet.Get()

@app.route('/')
def test():
    return "Hello World!"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
