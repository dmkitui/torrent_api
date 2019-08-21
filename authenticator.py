import pymongo
import os

MONGO_URI = os.environ.get('MONGO_URI')


def authenticate_request(token, password):
    print(str(token) + '   ' + str(password))
    client = pymongo.MongoClient(MONGO_URI)
    db = client['torrents']

    creds = db.authentications.find_one({'token': {'$exists': 1}})

    if creds:
        stored_token = creds['token']
        stored_password = creds['password']

        if token == stored_token and password == stored_password:
            return True
        else:
            return False

    else:
        return False

