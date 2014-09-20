from flask import Flask
from flask import request
from flask import Response
from Sublet import SubletEntity
from User import UserEntity
from Token import TokenEntity
from google.appengine.ext import ndb
import json
import geopy
import geopy.distance
import time
from datetime import datetime
from operator import itemgetter
app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def get_date(date_string):
    return datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y-%m-%d")))
def print_json(text):
    return Response(json.dumps(text), mimetype="application/json")

@app.route('/api/sublets/<int:sublet_id>', methods=['GET', 'PUT', 'DELETE'])
def api_sublet_with_id(sublet_id):
    sublet = SubletEntity.get_by_id(sublet_id)
    if sublet is None:
        return "Not Found", 404
    
    if request.method == 'GET':
        return print_json(sublet.Get())
    elif request.method == 'PUT':
        json_text = request.get_json()
        return print_json(sublet.Put(json_text))
    elif request.method == 'DELETE':
        return print_json(sublet.Delete())
           
@app.route('/api/sublets', methods=['GET', 'POST'])
def api_sublets():
    if request.method == 'POST':
        json_text = request.get_json()
        sublet = SubletEntity()
        return Response(json.dumps(sublet.Post(json_text)), mimetype="application/json"), 201
    elif request.method == 'GET':
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
        minimum_price = float(request.args.get("minimum_price", 0))
        maximum_price = float(request.args.get("maximum_price", 1000000))
        start_date = get_date(request.args.get("start_date"))
        end_date = get_date(request.args.get("end_date"))
        sort = request.args.get("sort", "distance")
        #geosearch
        center = geopy.Point(float(request.args.get("latitude")), float(request.args.get("longitude")))
        radius = float(request.args.get("radius"))
        #tags
        tag_text = request.args.get("tags", "")
        if tag_text == "":
            tags = []
        else:
            tags = tag_text.split(',')

            
        qry = SubletEntity.query(SubletEntity.price >= minimum_price,
                                 SubletEntity.price <= maximum_price,
                                 *[SubletEntity.tags == tag for tag in tags])
        sublets = qry.fetch()
        #should implement google's searches later
        infos = []
        for s in sublets:
            distance = geopy.distance.distance(geopy.Point(s.location.lat, s.location.lon), center).kilometers
            if distance <= radius and s.rooms_available > 0 and s.start_date <= start_date and s.end_date >= end_date:
                info = s.Get()
                info["distance"] = distance
                infos.append(info)
        
        infos = sorted(infos, key=itemgetter(sort))
        
        more = len(infos) > offset + limit
        #infos = [s.Get() for s in sublets[offset:offset + limit] if geopy.distance.distance(geopy.Point(s.location.lat, s.location.lon), center) <= radius]
        return print_json({"limit": limit, "offset": offset, "more": more, "sublets": infos[offset:offset + limit]})

@app.route('/api/users', methods=['POST'])
def api_users():
    if request.method == 'POST':
        json_text = request.get_json()
        user = UserEntity()
        return_data, token = user.Post(json_text)
        return_dict = {"user": return_data, "token": token}
        return print_json(return_dict), 201

def check_auth(username, password):
    accounts = UserEntity.query(UserEntity.email == username).fetch()
    if len(accounts) < 1:
        return False
    account = accounts[0]
    return account.CheckPassword(password), account

@app.route('/api/authenticate', methods=['POST', 'DELETE'])
def api_authenticate():
    if request.method == 'POST':
        auth = request.authorization
        if not auth:
            return 'Unauthorized', 401
        verified, account = check_auth(auth.username, auth.password)
        if not verified:
            return 'Unauthorized', 401
        return print_json({"user": account.Get(), "token": account.Login()})
    elif request.method =='DELETE':
        token_key = ndb.Key(urlsafe=request.args.get("token"))
        token_key.delete()
        return print_json({"status":"success"})
    
@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT'])
def api_users_with_id(user_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404
    
    if request.method == 'GET':
        return print_json(user.Get())

@app.route('/api/users/<int:user_id>/bookmarks', methods=['GET', 'POST'])
def api_users_bookmarks(user_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404

    if request.method == 'POST':
        user.InsertBookmark(request.get_json().get("sublet_id"))
        return print_json({"status":"success"})
    elif request.method == 'GET':
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 10)
        more = len(user.bookmarks) > offset + limit
        infos = []

        # clear deleted ones, inefficent but whatever >.>
        user.bookmarks = [bookmark for bookmark in user.bookmarks if not SubletEntity.get_by_id(bookmark) is None]
        user.put()
            
        for sublet_id in user.bookmarks[offset:offset + limit]:
            sublet = SubletEntity.get_by_id(sublet_id)
            infos.append(sublet.Get())
            
        return print_json({"limit": limit, "offset": offset, "more": more, "sublets": infos})
        
@app.route('/api/users/<int:user_id>/bookmarks/<int:sublet_id>', methods=['DELETE'])
def api_users_bookmarks_with_sublet_id(user_id, sublet_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404

    if request.method == 'DELETE':
        user.DeleteBookmark(sublet_id)
        return print_json({"status":"success"})
    
@app.route('/')
def test():
    return "Hello World!"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
