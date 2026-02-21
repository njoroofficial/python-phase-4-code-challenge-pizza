#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# get all restaurants

@app.route("/restaurants")
def get_restaurants():
    restaurants = Restaurant.query.all()
    return make_response(
        [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants],
        200,
    )

# get one restaurants
@app.route("/restaurants/<int:id>")
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    return make_response(restaurant.to_dict(), 200)


# delete a restaurant
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)


# get all pizzas
@app.route("/pizzas")
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response(
        [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas],
        200,
    )


# create a restaurant pizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return make_response(
            restaurant_pizza.to_dict(rules=('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')),
            201,
        )
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
