from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_restful import Api, Resource
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
api = Api(app)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(mongo_uri)
db = client.typingdb
users = db['Users']

def user_exists(uid):
    if users.count_documents({'uid': uid}) == 0:
        return False
    else:
        return True

def generate_return_dict(status, msg):
    ret_json = {
        'status': status,
        'msg': msg
    }
    return ret_json

def update_test_count(uid, increment):
    users.update_one({'uid': uid}, {'$inc': {'test_count': increment}})

def update_time_typing(uid, increment):
    users.update_one({'uid': uid}, {'$inc': {'test_time': increment}})

class UpdateTestCount(Resource):
    def post(self):
        posted_data = request.get_json()

        uid = posted_data['uid']
        increment = posted_data['test_count']

        if not user_exists(uid):
            return jsonify(generate_return_dict(301, 'Invalid User ID'))

        update_test_count(uid, increment)

        return jsonify(generate_return_dict(200, 'Test Count Updated'))

class AddUser(Resource):
    def post(self):
        posted_data = request.get_json()

        uid = posted_data['uid']

        # Check if user already exists
        if user_exists(uid):
            return jsonify(generate_return_dict(301, 'User Already Exists'))

        # Add user to database
        users.insert_one({'uid': uid ,'tests': [], 'test_count': 0, 'test_time': 0})

        return jsonify(generate_return_dict(200, 'User Added'))

class UpdateTimeTyping(Resource):
    def post(self):
        try:
            posted_data = request.get_json()

            uid = posted_data['uid']
            increment = posted_data['test_time']

            if not user_exists(uid):
                return jsonify(generate_return_dict(301, 'Invalid User ID'))

            update_time_typing(uid, increment)
            return jsonify(generate_return_dict(200, 'Time Updated'))

        except Exception as e:
            print(f"Error occurred: {e}")
            return {"status": "error", "message": str(e)}, 500

class StoreTestResult(Resource):

    def post(self):
        try:

            posted_data = request.get_json()

            uid = posted_data['uid']
            wpm = posted_data['wpm']
            raw_wpm = posted_data['raw_wpm']
            print(f"User ID: {uid}")
            if not user_exists(uid):
                print("User does not exist")
                return jsonify(generate_return_dict(301, 'Invalid User ID'))

            #New data base entry for the user
            users.update_one({
                'uid': uid
            }, {
                '$push': {
                    'tests': {
                        'wpm': wpm,
                        'raw_wpm': raw_wpm
                    }
                }
            } )

            return jsonify(generate_return_dict(200, 'Test Added'))
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"status": "error", "message": str(e)}, 500

class GetUserStats(Resource):
    def get(self, uid):
        try:
            user = users.find_one({'uid': uid}, {'_id': 0, 'test_count': 1, 'test_time': 1})

            if not user:
                    return jsonify(generate_return_dict(301, 'Invalid User ID'))
            return jsonify({
                    'status': 200,
                    'test_count': user['test_count'],
                    'test_time': user['test_time']
                })
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"status": "error", "message": str(e)}, 500

class GetTypingStats(Resource):
    def get(self, uid):
        try:
            user = users.find_one({'uid': uid}, {'_id': 0, 'tests': 1})

            if not user:
                return jsonify(generate_return_dict(301, 'Invalid User ID'))

            return jsonify({
                'status': 200,
                'tests': user['tests']
            })
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"status": "error", "message": str(e)}, 500

api.add_resource(UpdateTestCount, '/update_test_count')
api.add_resource(AddUser, '/add_user')
api.add_resource(UpdateTimeTyping, '/update_time_typing')
api.add_resource(StoreTestResult, '/store_test_result')
api.add_resource(GetUserStats, '/get_user_stats/<string:uid>')
api.add_resource(GetTypingStats, '/get_typing_stats/<string:uid>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
