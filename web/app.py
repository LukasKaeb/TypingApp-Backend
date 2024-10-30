from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_restful import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
api = Api(app)

client = MongoClient('mongodb://db:27017')
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
        posted_data = request.get_json()
        
        uid = posted_data['uid']
        increment = posted_data['test_time']

        if not user_exists(uid):
            return jsonify(generate_return_dict(301, 'Invalid User ID'))
        
        update_time_typing(uid, increment)
        return jsonify(generate_return_dict(200, 'Time Updated'))

class StoreTestResult(Resource):

    def post(self):
        try:

            posted_data = request.get_json()
        
            uid = posted_data['uid']
            wpm = posted_data['wpm']
            raw_wpm = posted_data['raw_wpm']
        
            if not user_exists(uid):
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

api.add_resource(UpdateTestCount, '/update_test_count')
api.add_resource(AddUser, '/add_user')       
api.add_resource(UpdateTimeTyping, '/update_time_typing')
api.add_resource(StoreTestResult, '/store_test_result')
       

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
