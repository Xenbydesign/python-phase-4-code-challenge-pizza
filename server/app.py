#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, g
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


@app.before_request
def before_request():
    if request.endpoint == "restaurantsbyid":
        id = request.view_args.get("id")
        rest = db.session.get(Restaurant, id)
        g.rest = rest


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        try:
            restaurants = [
                restaurant.to_dict(rules=("-restaurant_pizzas",))
                for restaurant in Restaurant.query
            ]
            return restaurants, 200
        except Exception as e:
            return {"error": str(e)}, 400


class RestaurantsById(Resource):
    def get(self, id):
        try:
            # if restaurant := db.session.get(Restaurant, id):
            # return restaurant.to_dict(), 200
            if g.rest:
                return g.rest.to_dict(), 200
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400

    def delete(self, id):
        try:
            # if restaurant := db.session.get(Restaurant, id):
            #     db.session.delete(restaurant)
            if g.rest:
                db.session.delete(g.rest)
                db.session.commit()
                return {}, 204
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400


class Pizzas(Resource):
    def get(self):
        try:
            pizzas = [
                pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in Pizza.query
            ]
            return pizzas, 200
        except Exception as e:
            return {"error": str(e)}, 400


class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_pizza = RestaurantPizza(**data)
            db.session.add(new_pizza)
            db.session.commit()
            return new_pizza.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            # return {"error": str(e)}, 400
            return {"errors": [str(e)]}, 400


api.add_resource(Restaurants, "/restaurants")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantsById, "/restaurants/<int:id>")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
