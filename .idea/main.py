from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import validate, fields, post_load
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://iotuser:iotuser@localhost/iot-test-db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    number_of_dishes = db.Column(db.Integer, unique=False)
    caloric = db.Column(db.Integer, unique=False)
    def __init__(self,name:str, number_of_dishes:int, caloric:int):
        self.name = name
        self.number_of_dishes = number_of_dishes
        self.caloric = caloric

class RecipeSchema(ma.Schema):
    name = fields.Str(validate=validate.Length(min=1, max=32))
    number_of_dishes = fields.Int(validate=validate.Range(min=1, max=9999))
    caloric = fields.Int(validate=validate.Range(min=1, max=9999))

    @post_load
    def make_recipe(self, data, **kwargs):
        return Recipe(**data)


recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

@app.route("/", methods=["GET"])
def get_recipe():
    recipes = Recipe.query.all()
    return jsonify(recipes_schema.dump(recipes))


@app.route("/<id>", methods=["GET"])
def get_recipe_id(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        abort(404)
    return jsonify(recipe_schema.dump(recipe))


@app.route("/", methods=["POST"])
def add_recipe():
    try:
        recipe = recipe_schema.load(request.json)
        db.session.add(recipe)
    except ValidationError as err:
        abort(400, err)
    db.session.commit()
    return jsonify(recipe_schema.dump(recipe))


@app.route("/<id>", methods=["DELETE"])
def delete_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        abort(404)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify(success=True)


@app.route("/<id>", methods=["PUT"])
def update_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        abort(404)
    try:
        recipe.name = request.json["name"]
        recipe.number_of_dishes = request.json["number_of_dishes"]
        recipe.caloric = request.json["caloric"]
    except ValidationError as err:
        abort(400, err)
    db.session.commit()
    return recipe_schema.jsonify(recipe)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)