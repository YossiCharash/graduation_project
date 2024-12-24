
from flask import Blueprint, jsonify, request, render_template

from databases.main import read_csv_, insert_new_csv_
from services.mongo_servic import analyze_attack_types, five_groups_deadliest, groups_participated_those_attacks, \
    groups_similar_preferences_goals, deadliest_average_by_region, change_number_attacks, sum_by_groups

Terrorists = Blueprint('Terrorists', __name__, template_folder="templates")


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





@Terrorists.route('/five_deadliest_groups',methods=['GET'])
def five_deadliest_groups():
    try:
        result = five_groups_deadliest()
        response_data = result.to_dict(orient='records')

        return jsonify(response_data),200

    except Exception as e:
        return e,500


@Terrorists.route('/groups_participated_those_attacks/',methods=['GET'])
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



# @Terrorists.route("/average_by_region")
# def deadliest_average_by_region_():
#     result = deadliest_average_by_region()
#     return render_template('casualty_markers_map.html')
#
# @Terrorists.route('/index_by_region', methods=['GET', 'POST'])
# def index_by_region():
#     return render_template('index.html', url_map="average_by_region")@Terrorists.route('/average', methods=['GET', 'POST'])
#
#
#
# @Terrorists.route('/change_number_attacks')
# def get_change_number_attacks():
#     result = change_number_attacks()
#     return render_template(result)
#
#
#
# @Terrorists.route('/index_change_number_attacks', methods=['GET', 'POST'])
# def index_change_number_attacks():
#     return render_template('index.html', url_map="change_number_attacks")@Terrorists.route('/average', methods=['GET', 'POST'])
#
#
#
# @Terrorists.route('/sum_by_groups')
# def get_sum_by_groups():
#     result = sum_by_groups()
#     return render_template(result)
#
#
#
# @Terrorists.route('/index_sum_by_groups', methods=['GET', 'POST'])
# def index_sum_by_groups():
#     return render_template('index.html', url_map="sum_by_groups")
#
#
#
