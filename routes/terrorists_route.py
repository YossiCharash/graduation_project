from flask import Blueprint, jsonify

from repositores.mongo import read_csv
from services.mongo_servic import analyze_attack_types

Terrorists = Blueprint('Terrorists', __name__)


@Terrorists.route("/init/",methods=['POST'])
def init_db():
    read_csv("data/globalterrorismdb_0718dist.csv")
    return jsonify("The database is created!")


@Terrorists.route("/the_deadliest/",methods=['GET'])
def the_deadliest():
    try:
        result = analyze_attack_types()
        return jsonify(result)

    except Exception as e:
        return e

