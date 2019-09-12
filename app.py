import pymongo
import os
import json
from flask import Flask, request, jsonify
from authenticator import authenticate_request
from flask_cors import CORS
from bson.objectid import ObjectId
from bson.json_util import dumps


MONGO_URI = os.environ.get('MONGO_URI')
app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient(MONGO_URI)
db = client['torrents']


@app.route("/torrent/", methods=['POST', 'GET'])
def torrent_action():
    token = request.headers.get('token')
    password = request.headers.get('password')

    if not authenticate_request(token, password):
        return jsonify({'message': 'Not authenticated'}), 401

    if request.method == 'GET':
        available_torrents = list(db.new_torrents.find({'status': 'fresh'}, {'_id': False}))
        data = db.authentications.find_one()

        action = request.headers.get('action')

        if action == 'free_space':
            return jsonify({'message': 'success', 'free_space': data['free_space']})

        else:
            if available_torrents:
                return jsonify({'message': 'success', 'torrents': available_torrents}), 200
            else:
                return jsonify({'message': 'Nothing to download now. Kuwa Mpole!'}), 400

    elif request.method == 'POST':
        magnet = request.headers.get('magnet')

        # try:
        if not magnet:
            return jsonify({'message': 'Magnet not supplied, jingoist!'}), 400

        action = request.headers.get('action')
        if action == 'downloaded':
            free_space = request.headers.get('free_space')
            db.new_torrents.find_one_and_update({'magnet': magnet}, {'$set': {'status': 'stale'}})
            db.authentications.find_one_and_update({"_id": ObjectId("5d5d630d7c213e60b8f25ec8")}, {"$set": {"free_space": free_space}})
            return jsonify(({'message': 'Torrent Updated'})), 200

        new_save = {'magnet': magnet, 'status': 'fresh'}

        try:
            db.new_torrents.save(new_save)
            return jsonify({'message': 'Success!'}), 201

        except pymongo.errors.DuplicateKeyError as e:
            return jsonify({'message': str(e)}), 409

        except Exception as e:
            return jsonify(({'message': str(e)})), 500

    else:
        return jsonify({'message': 'That Method is unsanctioned. Fuck off!'}), 400


if __name__ == "__main__":
    with app.app_context():
        client = pymongo.MongoClient(MONGO_URI)
        db = client['torrents']
        db.new_torrents.create_index([('magnet', 1)], unique=True)
    app.run()
