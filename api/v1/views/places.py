#!/usr/bin/python3
""" Places CRUD """
from flask import jsonify, abort, request
from models import storage
from models.city import City
from models.user import User
from models.place import Place
from api.v1.views import app_views
from models.state import State
from models.amenity import Amenity


@app_views.route("/cities/<city_id>/places", methods=["GET"],
                 strict_slashes=False)
def all_places(city_id):
    """Retrieves all places"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route("/places/<place_id>", methods=["GET"], strict_slashes=False)
def get_place(place_id):
    """Retrieves place by id"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route("/places/<place_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a place in city"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    if "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400
    user = storage.get(User, data["user_id"])
    if not user:
        abort(404)
    if "name" not in data:
        return jsonify({"error": "Missing name"}), 400
    data["city_id"] = city_id
    place = Place(**data)
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route("/places/<place_id>", methods=["PUT"], strict_slashes=False)
def update_place(place_id):
    """Updates a place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    for key, value in data.items():
        if key not in ["id", "user_id", "city_id", "created_at", "updated_at"]:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


# Searching
@app_views.route("/places_search", methods=["POST"],
                 strict_slashes=False)
def places_search():
    """Search places"""
    data = request.get_json()

    if data is None:
        abort(400, "Not a JSON")

    if not data or (not data.get("states") and not
                    data.get("cities") and not data.get("amenities")):
        places = storage.all(Place).values()
    else:
        places = []
        if data.get("states"):
            places.extend(get_places_from_states(data))

        if data.get("cities"):
            places = get_places_from_cities(places, data)

        if data.get("amenities"):
            if not places:
                places = storage.all(Place).values()
            places = filter_places_by_amenities(places, data["amenities"])
    # resolving the unserialized amenities issue
    places_dicts = [place.to_dict() for place in places]
    for place_dict in places_dicts:
        place_dict.pop('amenities', None)

    return jsonify(places_dicts)


def get_places_from_states(data):
    places = []
    for state_id in data["states"]:
        state = storage.get(State, state_id)
        if state:
            for city in state.cities:
                for place in city.places:
                    if place not in places:
                        places.append(place)
    return places


def get_places_from_cities(places, data):
    for city_id in data["cities"]:
        city = storage.get(City, city_id)
        if city:
            for place in city.places:
                if place not in places:
                    places.append(place)
    return places


def filter_places_by_amenities(places, amenity_ids):
    amenities = [storage.get(Amenity, amenity_id)
                 for amenity_id in amenity_ids]
    return [
        place
        for place in places
        if all(amenity in place.amenities for amenity in amenities)
    ]
