from flask import Flask
from flask import request
from flask import redirect
from Sublet import SubletEntity
from google.appengine.ext import ndb
app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/api/sublet/<int:sublet_id>', methods=['GET', 'PUT', 'DELETE'])
def api_sublet_with_id(sublet_id):
    sublet = SubletEntity.get_by_id(sublet_id)
    if sublet is None:
        return "Not Found", 404
    
    if request.method == 'GET':
        return sublet.Get(sublet_id)
    elif request.method == 'PUT':
        json = request.get_json()
        return sublet.Put(json)
    elif request.method == 'DELETE':
        return sublet.Delete()
           
@app.route('/api/sublet', methods=['GET', 'POST'])
def api_sublet():
    if request.method == 'POST':
        json = request.get_json()
        sublet = SubletEntity()
        return sublet.Post(json), 201
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
