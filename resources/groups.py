from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import mysql
from db_utils import *
from utils import *

class Groups(Resource):
	
	@jwt_required
	def get(self):

		_id = get_jwt_identity()

		query = "select permissionGroup from user where userID = " + str(_id)

		result = get_from_db(query)

		permission = result[0][0]

		if permission == 'ad':
			query = """Select grouptb.groupID, grouptb.groupName from grouptb"""

		else:
			query = """Select grouptb.groupID, grouptb.groupName
		 			from grouptb join group_user on group_user.groupID = grouptb.groupID where group_user.userID = """ + str(_id)

		result = get_from_db(query)

		final_list = []

		for row in result:
			new_result = {}
			new_result['groupID'] = row[0]
			new_result['groupName'] = row[1]
			final_list.append(new_result)

		return final_list

class Group(Resource):
	
	@jwt_required
	def get(self, _id=None):

		if not _id:
			return {'message':'Please provide the id of the group that you wish to get'}, 400

		query = "Select user.userID,user.username from user,group_user where user.userID = group_user.userID && group_user.groupID = " + str(_id)
		
		group_result = get_from_db(query)

		return {'result':group_result}

	@jwt_required
	def post(self, _id=None):

		user_id = get_jwt_identity()
		
		groups_parser = reqparse.RequestParser()
		groups_parser.add_argument('groupName',
		                          type=str,
		                          required=True,
		                          )

		data = groups_parser.parse_args()

		query = "SELECT MAX(groupID) FROM grouptb"
		result = get_one_from_db(query)
		
		maxID = check_max_id(result)

		query = "INSERT INTO grouptb VALUES (%s,%s)"

		post_to_db(query, (maxID,data['groupName']))

		query = "INSERT INTO group_user VALUES (%s,%s,%s)"

		post_to_db(query, (maxID,user_id,1))
		
		return {'groupID':maxID}, 201

	# @jwt_required
	# def delete(self, _id):

	# 	if not _id:
	# 		return {'message':'Please provide the id of the group that you wish to delete'}, 400

	# 	if(check_groups_db(_id)):
	# 		query = "DELETE FROM grouptb WHERE groupID=%s"
	# 		delete_from_db(query, (_id,))
	# 		return {'message':'Successfully deleted group with id: ' + str(_id)}, 200
	# 	else:
	# 		return {'message':'Cannot delete non-existing group'}, 400