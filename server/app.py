#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize Flask extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Get all heroes
class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes])

# Get hero by ID
class HeroDetail(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return make_response(jsonify({"error": "Hero not found"}), 404)

        hero_powers = [{"id": hp.id, "power_id": hp.power_id, "strength": hp.strength} for hp in hero.powers]

        return jsonify({
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": hero_powers
        })

# Get all powers
class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([{"id": power.id, "name": power.name, "description": power.description} for power in powers])

# Get power by ID
class PowerDetail(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)

        return jsonify({
            "id": power.id,
            "name": power.name,
            "description": power.description
        })

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)

        data = request.get_json()
        description = data.get("description")

        if description:
            power.description = description
            db.session.commit()
            return jsonify({
                "id": power.id,
                "name": power.name,
                "description": power.description
            })
        else:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

# Create HeroPower
class HeroPowerCreate(Resource):
    def post(self):
        data = request.get_json()
        hero_id = data.get("hero_id")
        power_id = data.get("power_id")
        strength = data.get("strength")

        if not all([hero_id, power_id, strength]):
            return make_response(jsonify({"errors": ["All fields are required"]}), 400)

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if not hero:
            return make_response(jsonify({"error": "Hero not found"}), 404)

        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)

        hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
        db.session.add(hero_power)
        db.session.commit()

        return jsonify({
            "id": hero_power.id,
            "hero": {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            },
            "power": {
                "id": power.id,
                "name": power.name,
                "description": power.description
            },
            "strength": hero_power.strength
        })

# Add resources to API
api.add_resource(Heroes, '/heroes')
api.add_resource(HeroDetail, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerDetail, '/powers/<int:id>')
api.add_resource(HeroPowerCreate, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
