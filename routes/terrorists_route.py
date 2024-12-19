from flask import Blueprint, jsonify

from databases.main import read_csv_
from services.mongo_servic import analyze_attack_types, deadliest_average_by_region

Terrorists = Blueprint('Terrorists', __name__)


@Terrorists.route("/init/",methods=['POST'])
def init_db():
    read_csv_("data/globalterrorismdb_0718dist.csv")
    return jsonify("The database is created!")


@Terrorists.route("/the_deadliest/<int:top>",methods=['GET'])
def the_deadliest(top=None):
    try:
        result = analyze_attack_types(top)
        return jsonify(result)

    except Exception as e:
        return e


@Terrorists.route("/average_by_region/<string:region>",methods=['GET'])
def average_by_region(region=None,top=None):
    try:
        result = deadliest_average_by_region(top=None)
        if result is None:
            return jsonify("The database is empty!")

        return jsonify(result), 200

    except Exception as e:
        return e,500