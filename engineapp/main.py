from flask import Flask
from flask import request
from flask import Response
from Sublet import SubletEntity
from User import UserEntity
from google.appengine.ext import ndb
import json
import geopy
import geopy.distance
app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
    

@app.route('/api/sublets/<int:sublet_id>', methods=['GET', 'PUT', 'DELETE'])
def api_sublet_with_id(sublet_id):
    sublet = SubletEntity.get_by_id(sublet_id)
    if sublet is None:
        return "Not Found", 404
    
    if request.method == 'GET':
        return Response(json.dumps(sublet.Get()), mimetype="application/json")
    elif request.method == 'PUT':
        json_text = request.get_json()
        return Response(json.dumps(sublet.Put(json_text)), mimetype="application/json")
    elif request.method == 'DELETE':
        return Response(sublet.Delete(), mimetype="application/json")
           
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
        more = len(sublets) > offset + limit
        #should implement google's searches later
        infos = []
        for s in sublets[offset:offset + limit]:
            distance = geopy.distance.distance(geopy.Point(s.location.lat, s.location.lon), center).kilometers
            if distance <= radius:
                info = s.Get()
                info["distance"] = distance
                infos.append(info)
        #infos = [s.Get() for s in sublets[offset:offset + limit] if geopy.distance.distance(geopy.Point(s.location.lat, s.location.lon), center) <= radius]
        return Response(json.dumps({"limit": limit, "offset": offset, "more": more, "sublets": infos}), mimetype="application/json")

@app.route('/api/users', methods=['POST'])
def api_users():
    if request.method == 'POST':
        json_text = request.get_json()
        user = UserEntity()
        return_data, token = user.Post(json_text)
        return_dict = {"user": return_data, "token": token}
        return Response(json.dumps(user.Post(return_dict)), mimetype="application/json"), 201
    
@app.route('/')
def test():
    return "Hello World!"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
