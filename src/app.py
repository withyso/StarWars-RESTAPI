"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#User Endpoints
@app.route('/user', methods=['GET'])
def handle_hello():
    all_users = User.query.all()
    users_serialized = []
    for user in all_users:
        users_serialized.append(user.serialize())
    print(users_serialized)
    return {'msg' : 'ok', 'data':users_serialized}, 200

#Generate single user using ID
@app.route('/user/<int:id>', methods=['GET'])
def get_single_user(id):
    #user1 = Person.query.get(person_id)
    single_user = User.query.get(id)
    print(single_user)
    if single_user is None:
        return {"Error" : "User ID doesn't exist"}, 404

    return jsonify({"data" : single_user.serialize()})

#Generate all characters
@app.route('/characters')
def get_all_characters(): 
    all_characters = Characters.query.all()
    all_characters_serialized = []

    for character in all_characters:
        all_characters_serialized.append(character.serialize_prev())

    print(all_characters_serialized)
    return {"data" : all_characters_serialized}

#Generate single character
@app.route('/characters/<int:id>', methods=['GET'])
def get_single_characters(id):
    single_character = Characters.query.get(id)
    
    if single_character is None:
        return jsonify({'Error': 'Character ID doesnt exist'}),404

    return jsonify({'data': single_character.serialize()})

#Create new character 


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
