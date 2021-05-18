from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

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


class RecipeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'number_of_dishes', 'caloric')


@app.route("/", methods=["GET"])
def get_recipe():
    recipes = Recipe.query.all()
    return jsonify(recipes_schema.dump(recipes))


@app.route("/<id>", methods=["GET"])
def get_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        abort(404)
    return jsonify(recipe_schema.dump(recipe))


@app.route("/", methods=["POST"])
def add_recipe():
    recipe = Recipe(name=request.json["name"], number_of_dishes=request.json["number_of_dishes"], caloric=request.json["caloric"])
    db.session.add(recipe)
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
    recipe.name = request.json["name"]
    recipe.number_of_dishes = request.json["number_of_dishes"]
    recipe.caloric = request.json["caloric"]
    db.session.commit()
    return jsonify(success=True)


if __name__ == '__main__':
    recipe_schema = RecipeSchema()
    recipes_schema = RecipeSchema(many=True)
    db.create_all()
    app.run(debug=True)