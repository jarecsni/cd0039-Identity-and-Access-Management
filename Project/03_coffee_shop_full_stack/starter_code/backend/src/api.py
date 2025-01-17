import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Initialise DB (needs to be commented out once the initialisation is done)
'''
#db_drop_and_create_all()

# ROUTES
'''
TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except Exception as exc:
        abort(exc.code if hasattr(exc, 'code') else 500, exc.description if hasattr(exc, 'description') else repr(exc))

'''
TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200    
    except Exception as exc:
        abort(exc.code if hasattr(exc, 'code') else 500, exc.description if hasattr(exc, 'description') else repr(exc))

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        post_data = request.get_json()

        if post_data.get('title', None) == None or post_data.get('recipe', None) == None:
            abort(422)
        
        title = post_data.get('title')
        recipe = post_data.get('recipe')
        recipe = json.dumps(recipe) if isinstance(recipe, list) else json.dumps([recipe])
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as exc:
        abort(exc.code if hasattr(exc, 'code') else 500, exc.description if hasattr(exc, 'description') else repr(exc))
        
'''
TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)

        data = request.get_json()
        drink.title = data['title'] if 'title' in data else drink.title
        drink.recipe = json.dumps(data['recipe']) if 'recipe' in data else drink.recipe
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as exc:
        abort(exc.code if hasattr(exc, 'code') else 500, exc.description if hasattr(exc, 'description') else repr(exc))


'''
TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)
    try:
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200
    except Exception as exc:
        abort(exc.code if hasattr(exc, 'code') else 500, exc.description if hasattr(exc, 'description') else repr(exc))

# Error Handling
'''
TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
TODO implement error handler for 404
    error handler should conform to general task above
'''
'''
TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(422)
@app.errorhandler(500)
@app.errorhandler(AuthError)
def handle_error(_error):
    if (isinstance(_error, AuthError)):
        code = _error.error['code']
        description = _error.error['description']
    else:
        code = _error.code if hasattr(_error, 'code') else 500
        description = _error.description if hasattr(_error, 'description') else repr(_error)
    return jsonify({
        "success": False,
        "error": code,
        "message": description
    }), code