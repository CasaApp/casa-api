from flask import Flask
from flask import request
from flask import Response
from Sublet import SubletEntity
from User import UserEntity
from Token import TokenEntity
from Image import ImageEntity
from google.appengine.ext import ndb
import json
import geopy
import geopy.distance
import time
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from functools import wraps
from flask import make_response
app = Flask(__name__)

def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def get_date(date_string):
    return datetime.fromtimestamp(time.mktime(time.strptime(date_string, "%Y-%m-%d")))
def print_json(text):
    return Response(json.dumps(text), mimetype="application/json")

@app.route('/api/sublets/<int:sublet_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
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
    return ""

@app.route('/api/sublets/<int:sublet_id>/images', methods=['POST', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_sublet_image(sublet_id):
    sublet = SubletEntity.get_by_id(sublet_id)
    if sublet is None:
        return "Not Found", 404
    if request.method == 'POST':
        file_data = request.files['image']
        image = file_data.read()
        if image:
            return print_json(sublet.AddImage(image))
        else:
            return "Bad Request", 400
    return ""

@app.route('/api/sublets/<int:sublet_id>/images/<int:image_id>', methods=['DELETE', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_sublet_image_with_image_id(sublet_id, image_id):
    sublet = SubletEntity.get_by_id(sublet_id)
    if sublet is None:
        return "Not Found", 404

    if request.method == 'DELETE':
        sublet.RemoveImage(image_id)
        return print_json(sublet.Get())
    return ""

@app.route('/api/images/<int:image_id>', methods=['GET', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_images(image_id):
    image = ImageEntity.get_by_id(image_id)
    if image is None:
        return "Not Found", 404

    return Response(image.image, mimetype="image/png")
           
@app.route('/api/sublets', methods=['GET', 'POST', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_sublets():
    if request.method == 'POST':
        auth = request.headers.get('Authorization')
        if auth is None:
            return 'Unauthorized', 401
        token_key = auth.split()[1]
        token = ndb.Key(urlsafe=token_key).get()
        #check if token is expired
        if datetime.now() > timedelta(seconds=token.EXPIRE_TIME) + token.creation_time:
            token.key.delete()
            return 'Unauthorized', 401
        
        user_id = token.user_id
        
        json_text = request.get_json()
        sublet = SubletEntity()
        return print_json(sublet.Post(json_text, token.user_id)), 201
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

        total_count = len(infos)
        more = total_count > offset + limit
        #infos = [s.Get() for s in sublets[offset:offset + limit] if geopy.distance.distance(geopy.Point(s.location.lat, s.location.lon), center) <= radius]
        return print_json({"limit": limit, "offset": offset, "more": more, "sublets": infos[offset:offset + limit], "total_count": total_count})
    return ""

@app.route('/api/users', methods=['POST', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_users():
    if request.method == 'POST':
        json_text = request.get_json()
        
        username = json_text.get("email")
        accounts = UserEntity.query(UserEntity.email == username).fetch(1)
        if len(accounts) > 0:
            return "Conflict", 409
        
        user = UserEntity()
        return_data, token = user.Post(json_text)
        return_dict = {"user": return_data, "token": token}
        return print_json(return_dict), 201
    return ""

def check_auth(username, password):
    accounts = UserEntity.query(UserEntity.email == username).fetch(1)
    if len(accounts) < 1:
        return False, None
    
    account = accounts[0]
    return account.CheckPassword(password), account

@app.route('/api/authenticate', methods=['POST', 'DELETE', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
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
    return ""
    
@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_users_with_id(user_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404
    
    if request.method == 'GET':
        return print_json(user.Get())
    return ""

@app.route('/api/users/<int:user_id>/bookmarks', methods=['GET', 'POST', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_users_bookmarks(user_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404

    if request.method == 'POST':
        user.InsertBookmark(request.get_json().get("sublet_id"))
        return print_json({"status":"success"})
    elif request.method == 'GET':
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        total_count = len(user.bookmarks)
        more = total_count > offset + limit
        infos = []

        # clear deleted ones, inefficent but whatever >.>
        user.bookmarks = [bookmark for bookmark in user.bookmarks if not SubletEntity.get_by_id(bookmark) is None]
        user.put()
            
        for sublet_id in user.bookmarks[offset:offset + limit]:
            sublet = SubletEntity.get_by_id(sublet_id)
            infos.append(sublet.Get())
            
        return print_json({"limit": limit, "offset": offset, "more": more, "sublets": infos, "total_count": total_count})
    return ""
        
@app.route('/api/users/<int:user_id>/bookmarks/<int:sublet_id>', methods=['DELETE', 'OPTIONS'])
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def api_users_bookmarks_with_sublet_id(user_id, sublet_id):
    user = UserEntity.get_by_id(user_id)
    if user is None:
        return "Not Found", 404

    if request.method == 'DELETE':
        user.DeleteBookmark(sublet_id)
        return print_json({"status":"success"})
    return ""
    
@app.route('/')
@add_response_headers({'Access-Control-Allow-Origin': '*', "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"})
def test():
    return "Hello World!"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
