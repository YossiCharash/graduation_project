
from flask import Blueprint, jsonify

from databases.main import read_csv_, insert_new_csv_
from services.mongo_servic import analyze_attack_types, five_groups_deadliest, groups_participated_those_attacks, \
    groups_similar_preferences_goals

Terrorists = Blueprint('Terrorists', __name__)


@Terrorists.route("/init/",methods=['POST'])
def init_db():
    # read_csv_("C:\\Users\\c0548\\PycharmProjects\\graduation_project\\data\\globalterrorismdb_0718dist.csv")
    insert_new_csv_('C:\\Users\\c0548\\PycharmProjects\\graduation_project\\data\\RAND_Database_of_Worldwide_Terrorism_Incidents.csv')
    return jsonify("The database is created!")


@Terrorists.route("/the_deadliest/<int:top>",methods=['GET'])
def the_deadliest(top=None):
    try:
        result = analyze_attack_types(top)

        response_data = result.to_dict(orient='records')

        return jsonify(response_data)

    except Exception as e:
        return e






# average_by_region()
@Terrorists.route('/five_deadliest_groups',methods=['GET'])
def five_deadliest_groups():
    try:
        result = five_groups_deadliest()
        response_data = result.to_dict(orient='records')

        return jsonify(response_data),200

    except Exception as e:
        return e,500


@Terrorists.route('/groups_participated_those_attacks',methods=['GET'])
def get_groups_participated_those_attacks():
    try:
        result = groups_participated_those_attacks()
        return jsonify(result), 200

    except Exception as e:
        return e,500


@Terrorists.route('/groups_similar_preferences_goals',methods=['GET'])
def get_groups_similar_preferences_goals():
    try:
        result = groups_similar_preferences_goals()
        return jsonify(result), 200
    except Exception as e:
        return e,500


@Terrorists.route("/average_by_region/<string:region>",methods=['GET'])
def average_by_region(region=None,top=None):
    try:
        result = analyze_attack_types(top)

        return jsonify(result), 200

    except Exception as e:
        return e,500


# deadliest_average_by_region()
# change_number_attacks()
# sum_by_grops()
# groups_common_goals('region')
# areas_common_attack_strategies_by_groups('region')
# identify_areas_with_high_intergroup_activity('region')