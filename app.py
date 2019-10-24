import pymongo
import os
from flask import Flask, request, jsonify, make_response, render_template
from flask_moment import Moment
from flask_cors import CORS
from bson.objectid import ObjectId
from functools import wraps
from datetime import datetime

MONGO_URI = os.environ.get('MONGO_URI')
API_KEY = os.environ.get('API_KEY')
DELETE_URL = os.environ.get('DELETE_URL')
ENV = os.environ.get('ENV')

app = Flask(__name__)
moment = Moment(app)
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
        data = db.free_space.find_one()
        action = request.headers.get('action')

        if action == 'free_space':
            return _corsify_res(jsonify({'message': 'success', 'free_space': data['disk_info']}))

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
            db.new_torrents.find_one_and_update({'magnet': magnet}, {'$set': {'status': 'stale'}})
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
        data = request.get_json()

        files = data['files']
        disk_info = data['disk_info']

        try:
            db.router_files.insert(dict(files))
        except pymongo.errors.DuplicateKeyError:
            db.router_files.replace_one({}, dict(files))

        db.free_space.find_one_and_update({"_id": ObjectId("5d88eb2d4d9bb5e32fe35efa")}, {"$set": {"disk_info": disk_info}})

        return _corsify_res(jsonify({'message': 'Success...'})), 200

    elif request.method == 'GET':

        file_tree = db.router_files.find_one({})
        disk_info = db.free_space.find_one({})['disk_info']

        if file_tree:
            files = {
                'type': 'directory',
                'name': 'Home Router Files',
                 'children': file_tree['children'],
                 'path': './',
                 'status': 'READONLY'
            }

            return render_template('home.html', file_tree=files, disk_info=disk_info,
                                   credentials={'DELETE_URL': DELETE_URL,
                                                'API_KEY': API_KEY,
                                                'ENV': ENV})
        else:
            return render_template('home_empty.html')


@app.route("/delete-files/", methods=['POST', 'GET'])
@authenticate
def delete_one():
    if request.method == 'POST':
        delete_path = request.headers.get('Delete-Path')
        if delete_path:
            current_files = db.router_files.find_one({})

            def update_deleted(file_tree, to_delete):
                for k, v in file_tree.items():
                    if k == 'path' and v == to_delete:
                        file_tree['status'] = 'deleted'
                        if file_tree['type'] == 'directory':
                            update_children(file_tree['children'])
                        return True
                    elif k == 'children':
                        if isinstance(v, list):
                            for x in v:
                                if update_deleted(x, to_delete):
                                    return True
                    else:
                        continue

            def update_children(children):
                for item in children:
                    item['status'] = 'deleted'
                    if item['type'] == 'directory':
                        update_children(item['children'])

            update_status = update_deleted(current_files, delete_path)
            if update_status:
                try:
                    db.router_files.replace_one({}, current_files)
                    return _corsify_res(jsonify({'message': 'Update Successful'})), 201
                except Exception as e:
                    return _corsify_res(jsonify({'message': 'Update Error:' + str(e)})), 500

        else:
            return _corsify_res(jsonify({'message': 'Some issue...'})), 400

    elif request.method == 'GET':
        current_files = db.router_files.find_one({})
        deleted_files = []

        def get_deleted_files(file_tree):
            for k, v in file_tree.items():
                if k == 'status' and v == 'deleted':
                    deleted_files.append(file_tree['path'])

                elif k == 'children':
                    if isinstance(v, list):
                        for x in v:
                            get_deleted_files(x)
                else:
                    continue

        if current_files:
            get_deleted_files(current_files)

        if deleted_files:
            return _corsify_res(jsonify({'message': 'Some files to delete', 'files_to_delete': deleted_files})), 200
        else:
            return _corsify_res(jsonify({'message': 'No files to delete'})), 200


def _cors_prelight_res():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_res(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(timestamp):
    """Timestamp to datetime"""
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp)


if __name__ == "__main__":
    with app.app_context():
        db.new_torrents.create_index([('magnet', 1)], unique=True)
        db.router_files.create_index([('path', 1), ('size', 1)], unique=True)
    app.run()
