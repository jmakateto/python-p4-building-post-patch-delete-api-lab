from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return "<h1>Bakery GET-POST-PATCH-DELETE API</h1>"


@app.route("/bakeries")
def bakeries():
    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]
    response = make_response(bakeries_serialized, 200)
    return response


@app.route("/bakeries/<int:id>", methods=["GET", "PATCH"])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if request.method == "GET":
        bakery_serialized = bakery.to_dict()
        response = make_response(bakery_serialized, 200)
        return response
    elif request.method == "PATCH":
        data = request.form
        new_name = data.get("name")

        if not new_name:
            return jsonify({"error": "Invalid data provided"}), 400

        try:
            bakery.name = new_name
            db.session.commit()
            return jsonify(bakery.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to update bakery - {str(e)}"}), 500


@app.route("/baked_goods", methods=["POST"])
def create_baked_good():
    data = request.form
    name = data.get("name")
    price = data.get("price")
    bakery_id = data.get("bakery_id")

    if not name or not price or not bakery_id:
        return jsonify({"error": "Invalid data provided"}), 400

    try:
        new_baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)
        db.session.add(new_baked_good)
        db.session.commit()
        return jsonify(new_baked_good.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create baked good - {str(e)}"}), 500


@app.route("/baked_goods/<int:id>", methods=["DELETE"])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)

    if baked_good is None:
        return jsonify({"error": "Baked good not found"}), 404

    try:
        db.session.delete(baked_good)
        db.session.commit()
        return jsonify({"message": "Baked good deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete baked good - {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5555, debug=True)
