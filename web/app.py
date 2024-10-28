from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.typingdb
users = db['Users']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)