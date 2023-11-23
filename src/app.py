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
from models import db, User, Planets, Characters, Favorites

# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route("/")
def sitemap():
    return generate_sitemap(app)


# USERS

@app.route("/user", methods=["GET"])
def get_all_users():
    try:
        get_all_users = User.query.all()
        return [user.serialize() for user in get_all_users]
    
    except ValueError as err:
        return {"message": "failed to retrieve list of users" + err}, 500


# @app.route("/user/<int:user_id>", methods=["GET"])
# def get_user_by_id(user_id):
#     try:
#         selected_user = User.query.get(user_id) or None
#         if selected_user == None:
#             return {"message": f"User with the id {user_id} doesn't exist"}, 400
#         else:
#             return selected_user.serialize()

#     except ValueError as err:
#         return {"message": f"Failed to retrieve user with the id {user_id} " + err}, 500


# PEOPLE


@app.route("/people", methods=["GET"])
def get_all_people():
    try:
        all_people = Characters.query.all()
        return [character.serialize() for character in all_people]

    except ValueError as err:
        return {"message": f"Failed to retrieve list of characters " + err}, 500


@app.route("/people/<int:people_id>", methods=["GET"])
def get_people_by_id(people_id):
    try:
        selected_character = Characters.query.get(people_id) or None
        if selected_character == None:
            return {"message": f"Character with the id {people_id} doesn't exist"}, 400
        else:
            return selected_character.serialize()

    except ValueError as err:
        return {
            "message": f"Failed to retrieve character with the id {people_id} " + err
        }, 500


# PLANETS


@app.route("/planets", methods=["GET"])
def get_all_planets():
    try:
        all_planets = Planets.query.all()
        return [planet.serialize() for planet in all_planets]

    except ValueError as err:
        return {"message": "Failed to retrieve list of planets " + err}, 500


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet_by_id(planet_id):
    try:
        selected_planet = Planets.query.get(planet_id) or None
        if selected_planet == None:
            return {"message": f"Planet with the id {planet_id} doesn't exist"}, 400
        else:
            return selected_planet.serialize()

    except ValueError as err:
        return {
            "message": f"Failed to retrieve planet with the id {planet_id} " + err
        }, 500


# FAVORITES


@app.route("/users/favorites", methods=["GET"])
def get_favorites_list(user_id):
    try:
        user_favorites_list = Favorites.query.filter(Favorites.user_id == user_id)
        return [favorite.serialize() for favorite in user_favorites_list]

    except ValueError as err:
        return {
            "message": f"Failed to retrieve list of favorite from the user id {user_id}"
            + err
        }, 500


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet_by_id(user_id, planet_id):
    try:
        planet = Planets.query.get(planet_id)
        selected_planet = Favorites.query.filter(
            Favorites.planet_id == planet_id, Favorites.user_id == user_id
        )
        selected_planet = [planet.serialize() for planet in selected_planet]
        if selected_planet:
            return {
                "message": f"{selected_planet[0]['people']} is now on favorites list"
            }
        elif not planet:
            return {"message": f"Character with id: {planet_id} doesn't exist"}
        else:
            add_new_favorite_planet = Favorites(
                user_id=user_id, planet_id=planet_id, planet=planet
            )
            db.session.add(add_new_favorite_planet)
            db.session.commit()
            return add_new_favorite_planet.serialize(), 200

    except ValueError as err:
        return {"message": f"Failed to add planet with the id {planet_id}" + err}, 500


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_planet_from_favorites(user_id, planet_id):
    try:
        selected_planet_from_favorites = Favorites.query.filter(
            Favorites.user_id == user_id, Favorites.planet_id == planet_id
        )
        for favorite in selected_planet_from_favorites:
            db.session.delete(favorite)
        db.session.commit()

        user_favorites_list = Favorites.query.filter(Favorites.user)
        return [favorite.serialize() for favorite in user_favorites_list]

    except ValueError as err:
        return {
            "message": f"Failed to delete planet with the id {planet_id}" + err
        }, 500


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_character_by_id(user_id, people_id):
    try:
        character = Characters.query.get(people_id)
        selected_character = Favorites.query.filter(
            Favorites.people_id == people_id, Favorites.user_id == user_id
        )
        selected_character = [people.serialize() for people in selected_character]
        if selected_character:
            return {
                "message": f"{selected_character[0]['people']} is now on favorites list"
            }
        elif not character:
            return {"message": f"Character with id: {people_id} doesn't exist"}
        else:
            add_new_favorite_character = Favorites(
                user_id=user_id, people_id=people_id, people=character
            )
            db.session.add(add_new_favorite_character)
            db.session.commit()
            return add_new_favorite_character.serialize(), 200

    except ValueError as err:
        return {
            "message": f"Failed to add character with the id {people_id}" + err
        }, 500


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_character_from_favorites(user_id, people_id):
    try:
        selected_character_from_favorites = Favorites.query.filter(
            Favorites.user_id == user_id, Favorites.people_id == people_id
        )
        for favorite in selected_character_from_favorites:
            db.session.delete(favorite)
        db.session.commit()

        user_favorites_list = Favorites.query.filter(Favorites.user)
        return [favorite.serialize() for favorite in user_favorites_list]

    except ValueError as err:
        return {
            "message": f"Failed to delete character with the id {people_id}" + err
        }, 500


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
