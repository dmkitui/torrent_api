import pymongo
import os
from flask import Flask, request, jsonify, make_response
from authenticator import authenticate_request
from flask_cors import CORS
from bson.objectid import ObjectId
from functools import wraps

MONGO_URI = os.environ.get('MONGO_URI')
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient(MONGO_URI)
db = client['torrents']


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return _cors_prelight_res()
        auth = request.headers.get('X-Api-Key')

        if not auth or auth != API_KEY:
            return _corsify_res(jsonify({'message': 'Not authenticated'})), 401
        return f(*args, **kwargs)
    return wrapper


@app.route("/torrent/", methods=['POST', 'GET', 'OPTIONS'])
@authenticate
def torrent_action():

    if request.method == 'GET':
        available_torrents = list(db.new_torrents.find({'status': 'fresh'}, {'_id': False}))
        data = db.authentications.find_one()

        action = request.headers.get('action')

        if action == 'free_space':
            return _corsify_res(jsonify({'message': 'success', 'free_space': data['free_space']}))

        else:
            if available_torrents:
                return _corsify_res(jsonify({'message': 'success', 'torrents': available_torrents})), 200
            else:
                return _corsify_res(jsonify({'message': 'Nothing to download now. Kuwa Mpole!'})), 400

    elif request.method == 'POST':
        magnet = request.headers.get('magnet')

        # try:
        if not magnet:
            return _corsify_res(jsonify({'message': 'Magnet not supplied, jingoist!'})), 400

        action = request.headers.get('action')
        if action == 'downloaded':
            free_space = request.headers.get('free_space')
            db.new_torrents.find_one_and_update({'magnet': magnet}, {'$set': {'status': 'stale'}})
            db.authentications.find_one_and_update({"_id": ObjectId("5d5d630d7c213e60b8f25ec8")}, {"$set": {"free_space": free_space}})
            return _corsify_res(jsonify(({'message': 'Torrent Updated'}))), 200

        new_save = {'magnet': magnet, 'status': 'fresh'}

        try:
            db.new_torrents.save(new_save)
            return _corsify_res(jsonify({'message': 'Success!'})), 201

        except pymongo.errors.DuplicateKeyError as e:
            return _corsify_res(jsonify({'message': str(e)})), 409

        except Exception as e:
            return _corsify_res(jsonify(({'message': str(e)}))), 500

    else:
        return _corsify_res(jsonify({'message': 'That Method is unsanctioned. Fuck off!'})), 400


@app.route("/files/", methods=['POST', 'GET', 'OPTIONS'])
@authenticate
def file_manager():
    if request.method == 'POST':
        files = request.get_json()
        for dir_data in files:
            dir_data['deleted'] = False
        try:
            db.router_files.insert_many(files)
        except pymongo.errors.DuplicateKeyError:
            pass

        return _corsify_res(jsonify({'message': 'Success...'})), 200

    elif request.method == 'GET':
        pass



def _cors_prelight_res():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_res(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    with app.app_context():
        client = pymongo.MongoClient(MONGO_URI)
        db = client['torrents']
        db.new_torrents.create_index([('magnet', 1)], unique=True)
        db.router_files.create_index([('path', 1), ('size', 1)], unique=True)
    app.run()
