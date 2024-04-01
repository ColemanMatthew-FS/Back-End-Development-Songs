from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200
    # return{"status":"OK"}, 200
    
@app.route("/count")
def count():
    count = db.songs.count_documents({})
    # return {"count": count}, 200
    return jsonify(dict(count = count)), 200

@app.route("/song", methods=["GET"])
def songs():
    results = list(db.songs.find({}))
    # return {"songs": parse_json(results)}, 200
    return jsonify(dict(songs = parse_json(results))), 200

@app.route("/song/<id>", methods=["GET"])
def get_song_by_id(id):
    result = db.songs.find_one({"id": int(id)})
    if result:
        return jsonify(dict(song=parse_json(result))), 200
    return jsonify(dict(message="song with id not found")), 404

@app.route("/song", methods=["POST"])
def create_song():
    new_song = request.json
    if db.songs.find_one({"id": new_song["id"]}):
        return jsonify(dict(Message="song with id {} already present".format(new_song["id"]))), 302
    db.songs.insert_one(new_song)
    result = db.songs.find_one({"id": new_song["id"]})
    return jsonify({"inserted id":parse_json(result["_id"])})

@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    update = request.json
    changes = {"$set":update}
    if db.songs.find_one({"id":id}):
        result = db.songs.update_one({"id":id}, changes)
        if result.modified_count == 0:
            return jsonify(dict(message="song found, but nothing updated")), 200
        updated_song = db.songs.find_one({"id":id})
        return parse_json(updated_song), 201
    return jsonify(dict(message="song not found"))

@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    result = db.songs.delete_one({"id":id})
    if result.deleted_count == 0:
        return jsonify(dict(message="song not found")), 404
    return {}, 204