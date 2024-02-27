#!/usr/bin/python3
""" Reviews CRUD """
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.review import Review
from models.user import User
from api.v1.views import app_views


@app_views.route("/places/<place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def all_reviews(place_id):
    """Retrieves all reviews"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route("/reviews/<review_id>", methods=["GET"], strict_slashes=False)
def get_review(review_id):
    """Retrieves review by id"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route("/reviews/<review_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    storage.delete(review)
    storage.save()
    return jsonify({}), 200


@app_views.route("/places/<place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def create_review(place_id):
    """Creates reeview"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    req_body = request.get_json()
    if not req_body:
        return jsonify({"error": "Not a JSON"}), 400
    if "user_id" not in req_body:
        return jsonify({"error": "Missing user_id"}), 400
    user = storage.get(User, req_body["user_id"])
    if not user:
        abort(404)
    if "text" not in req_body:
        return jsonify({"error": "Missing text"}), 400
    req_body["place_id"] = place_id
    review = Review(**req_body)
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route("/reviews/<review_id>", methods=["PUT"], strict_slashes=False)
def update_review(review_id):
    """Updates review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    req_body = request.get_json()
    if not req_body:
        return jsonify({"error": "Not a JSON"}), 400
    for key, value in req_body.items():
        if key not in ["id", "user_id", "place_id", "created_at",
                       "updated_at"]:
            setattr(review, key, value)
    review.save()
    return jsonify(review.to_dict()), 200
