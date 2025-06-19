from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate

from models import db, Pet

# create a Flask application instance
app = Flask(__name__)

# configure the database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# configure flag to disable modification tracking and use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# initialize the Flask application to use the database
db.init_app(app)

# CRUD routes for Pet model

@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    pets_list = [{'id': pet.id, 'name': pet.name, 'species': pet.species} for pet in pets]
    return jsonify(pets_list), 200

@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="Pet not found")
    return jsonify({'id': pet.id, 'name': pet.name, 'species': pet.species}), 200

@app.route('/pets', methods=['POST'])
def create_pet():
    data = request.get_json()
    if not data or 'name' not in data or 'species' not in data:
        abort(400, description="Missing required fields: name and species")
    new_pet = Pet(name=data['name'], species=data['species'])
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({'id': new_pet.id, 'name': new_pet.name, 'species': new_pet.species}), 201

@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="Pet not found")
    data = request.get_json()
    if not data:
        abort(400, description="Missing JSON data")
    pet.name = data.get('name', pet.name)
    pet.species = data.get('species', pet.species)
    db.session.commit()
    return jsonify({'id': pet.id, 'name': pet.name, 'species': pet.species}), 200

@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None:
        abort(404, description="Pet not found")
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': f'Pet {pet_id} deleted'}), 200


@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Pet API',
        'endpoints': {
            'GET /pets': 'List all pets',
            'GET /pets/<pet_id>': 'Get a pet by ID',
            'POST /pets': 'Create a new pet',
            'PUT /pets/<pet_id>': 'Update a pet by ID',
            'DELETE /pets/<pet_id>': 'Delete a pet by ID'
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found', 'message': str(error)}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
