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
from models import db, User, Planets, Characters, FavoritePlanets, FavoriteCharacters
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

#--- Character Endpoints ---#
#Generate all characters
@app.route('/characters')
def get_all_characters(): 
    all_characters = Characters.query.all()
    all_characters_serialized = []

    for character in all_characters:
        all_characters_serialized.append(character.serialize_id_name())

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
@app.route('/create/character', methods=['POST'])
def create_character():
    body = request.get_json(silent=True)
    new_character = Characters()
    if body is None:
        return jsonify({'Msg': 'Body must contain name and height as mandatory fields, mass and gender are not required'}),400
    if 'name' not in body:
        return jsonify({'Msg': 'Body field is required'}), 400
    if 'height' not in body:
        return jsonify({'msg': 'height field is required'}), 400
    if body['gender'] == 'male' or 'female':
        new_character.gender = body['gender']
    if body['mass'] > 0: 
        new_character.mass = body['mass']
    new_character.name = body['name']
    new_character.height = body['height']
    db.session.add(new_character)
    db.session.commit()

    return jsonify({'Msg': 'New character created', 
                    'data': new_character.serialize()})

#Delete Character
@app.route('/delete/character/<int:id>', methods=['DELETE'])
def delete_character(id):
    character_to_delete = Characters.query.get(id)
    if character_to_delete is None:
        return jsonify({'Msg' : 'Character ID doesnt exist'}), 404
    db.session.delete(character_to_delete)
    db.session.commit()

    return jsonify({'Msg' : f'Planet with name {character_to_delete.name} was deleted'})
#--------------------------------------------------#

#--- Planets endpoints ---#
#Generate all planets
@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planets.query.all()
    all_planets_serialized = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify({'Msg': 'Ok', 'data' : all_planets_serialized}), 200

#Generate single planet
@app.route('/planet/<int:id>', methods=['GET'])
def get_single_planet(id):
    single_planet = Planets.query.get(id)
    print(single_planet)
    if single_planet is None: 
        return jsonify ({'Error' : "ID planet doesn't exist, please try with diferent id"}), 404

    return jsonify({'Msg': 'Ok', 'Data' : single_planet.serialize()}), 200

#Create new planet
@app.route('/create/planet', methods=['POST'])
def create_new_planet():
    body = request.get_json(silent=True)
    print(body)
    new_planet = Planets()
    if body is None:
        return jsonify({'Msg' : 'Body must not be empty, please fill will all the info'}), 400
    if 'name' not in body:
        return jsonify({'Msg' : 'Please add planet name'}), 400
    if 'population' not in body:
        return jsonify({'Msg' : 'Please add planet population'}), 400
    new_planet.name = body['name']
    new_planet.population = body['population']
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({'Msg' : 'Planet created',
                    'data' : new_planet.serialize()})

#Delete Planet
@app.route('/delete/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet_to_delete = Planets.query.get(id)
    print(planet_to_delete)
    if planet_to_delete is None: 
        return jsonify({'Error': 'Planet ID doesnt found'}), 404
    db.session.delete(planet_to_delete)
    db.session.commit()

    return jsonify({'Msg' : f'Planet with name {planet_to_delete.name} was deleted'})
#--------------------------------------------------#

#--- Favorite planets and characters endpoints ---#

#Get user favorites
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None: 
        return jsonify({'Msg' : f'User with ID {user_id} doesnt exist'}), 404
    favorite_user_planets = FavoritePlanets.query.filter_by(user_id = user_id).all()
    if len(favorite_user_planets) <= 0:
        return jsonify({'Msg': f'User with ID {user_id} doesnt have favorites'})
    
#Query to get planets favorites
    favorite_planets = db.session.query(FavoritePlanets, Planets).join(Planets).filter(FavoritePlanets.user_id == user_id).all()
    user_favorite_planets_serialized = []
    for favorite_planet, planet in favorite_planets:
        user_favorite_planets_serialized.append({
            'favorite_planet_id': favorite_planet.id,
            'planet_detail': planet.serialize(),
        })

#Query to get character favorites
    favorite_characters = db.session.query(FavoriteCharacters, Characters).join(Characters).filter(FavoriteCharacters.user_id == user_id).all()
    user_favorite_characters_serialized = []
    for favorite_character, character in favorite_characters:
        user_favorite_characters_serialized.append({
            'favorite_character_id': favorite_character.id,
            'character_detail': character.serialize_id_name()
        })
    print(user_favorite_characters_serialized)
    
    return jsonify({'msg' : 'Ok', 
                    'favorite_planets': user_favorite_planets_serialized, 
                    'favorite_characters': user_favorite_characters_serialized}), 200

#Add new character to favorites
@app.route('/user/<int:user_id>/favorite/add/character', methods=['POST'])
def user_new_character_favorite(user_id):
    body = request.get_json(silent=True)
    user = User.query.get(user_id)
    character = Characters.query.get(body['character_id'])
    user_favorites = FavoriteCharacters.query.all()
    user_favorites_serialized = list(map(lambda userfav: userfav.serialize(), user_favorites))
    if body is None: 
        return jsonify({'error' : 'Body must contain info'}), 400
    if 'character_id' not in body:
        return jsonify({'error' : 'Body must contain character_id'}), 400
    if user is None: 
        return jsonify({'msg' : 'user ID doesnt exist'}),400
    if character is None: 
        return jsonify({'msg' : 'Character ID doesnt exist'}), 400
    new_favorite = FavoriteCharacters()
    new_favorite.user_id = user_id
    new_favorite.character_id = body['character_id']
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({'msg' : 'New character added to favorite', 'success' : new_favorite.serialize()})

#Delete character from favorites
@app.route('/user/<int:user_id>/favorite/delete/character', methods=['DELETE'])
def delete_character_favorite(user_id):
    user = User.query.get(user_id)
    body = request.get_json(silent=True)
    id_favorite = body['favorite_id']
    favorite = FavoriteCharacters.query.get(id_favorite)
    if body is None:
        return jsonify({'msg': 'Body must have id of the favorite'}), 400
    if 'favorite_id' not in body:
        return jsonify({'msg' : 'You should send the id of favorite_character_id Key to proceed'}), 400
    if user is None: 
        return jsonify({'msg' : 'User doesnt exist, check ID'}), 400
    if favorite is None: 
        return jsonify({'msg' : 'ID from favorites doesnt exist'}), 400

    return jsonify({'Msg' : 'Character from favorites deleted', 'success' : favorite.serialize()})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
