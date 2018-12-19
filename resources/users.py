from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
    get_current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
from db import mysql
from db_utils import *
from utils import *
import json

def find_by_name(username):

	query = "SELECT * FROM user WHERE username=%s"
	result = get_from_db(query, (username,))

	for row in result:
		if row[1] == username:
			return True, row
	
	return False, None

def check_user_db(_id):

	query = "SELECT * FROM user WHERE userID=%s"
	result = get_from_db(query, (_id,))

	for row in result:
		if row[0] == _id:
			return True
	
	return False

class UserRegister(Resource):

	def post(self):

		user_parser = reqparse.RequestParser()
		user_parser.add_argument('username',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('password',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('sex',
		                          type=str,
		                          required=False,
		                          )
		user_parser.add_argument('age',
		                          type=int,
		                          required=False,
		                          )
		user_parser.add_argument('motivation',
		                          type=str,
		                          required=False,
		                          )
		data = user_parser.parse_args()

		find_user, user = find_by_name(data['username'])

		if find_user:
			return {'message':'A user with that name already exists!'}, 400

		query = "SELECT MAX(userID) FROM user"
		result = get_one_from_db(query)
		
		maxID = check_max_id(result)

		sex = data['sex'] if 'sex' in data else ''
		age = data['age'] if 'age' in data else 0
		motivation = data['motivation'] if 'motivation' in data else ''

		query = "INSERT INTO user VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

		salted_password = generate_password_hash(data['password'])

		post_to_db(query, (maxID,data['username'],salted_password,'key','reset','us',0,None,sex,age,motivation))
		
		return {'message':'Successfully registered!'}, 201

class UserLogin(Resource):

	def post(self):

		user_parser = reqparse.RequestParser()
		user_parser.add_argument('username',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('password',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()

		find_user, user = find_by_name(data['username'])
		if find_user:
			if check_password_hash(user[2],data['password']): # userID, username, password -- 0,1,2
				put_in_blacklist(user[0])
				access_token = create_access_token(identity=user[0], expires_delta=False)
				return {
					'access_token': access_token,
					'permissions': user[5],
					'id':user[0]
				}, 200

		return {'message':'Invalid credentials!'}, 401

class UserLogout(Resource):

	@jwt_required
	def post(self):

		user_id = get_jwt_identity()
		put_in_blacklist(user_id)
		
		return {"message": "Successfully logged out"}, 200

class ResetPassword(Resource):

	@jwt_required
	def post(self):

		user_parser = reqparse.RequestParser()
		user_parser.add_argument('userID',
		                          type=int,
		                          required=True,
		                          )
		user_parser.add_argument('pw',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()

		pw = generate_password_hash(data['pw'])

		query = "UPDATE user SET password=%s WHERE userID=" + str(data['userID'])

		post_to_db(query, (pw,))

		return {'message':'Successfully reset the password'}, 201

class Users(Resource):

	@jwt_required
	def get(self):

		query = "SELECT * FROM user"
		result = get_from_db(query)

		final_list = []

		for row in result:
			new_item = {}
			new_item['id'] = row[0]
			new_item['username'] = row[1] 
			new_item['permissions'] = row[5]
			new_item['gender'] = row[7]
			new_item['age'] = row[8]
			new_item['motivation'] = row[9]
			final_list.append(new_item)

		return final_list

class User(Resource):

	@jwt_required
	def get(self, _id):

		query = "SELECT userID,username,sex,age,motivation FROM user WHERE userID=" + str(_id)

		result = get_from_db(query)

		if result:
			return_item = {}
			return_item['id'] = result[0][0]
			return_item['username'] = result[0][1]
			return_item['sex'] = result[0][2]
			return_item['age'] = result[0][3]
			return_item['motivation'] = result[0][4]
			return return_item
		else:
			return {'message':'No user with this ID found'}, 400

	@jwt_required
	def delete(self, _id):

		if not _id:
			return {'message':'Please provide the id of the user that you wish to delete'}, 400

		if not check_user_db(_id):
			return {'message':'cannot delete non-existing person'}, 400

		user_id = get_jwt_identity()

		query = "SELECT permissionGroup from user where userID = " + str(user_id)
		permission = get_from_db(query)

		if not permission:
			return {'Message':'Not a valid user'}, 400

		permission = permission[0][0]

		if not permission == 'ad':
			return {'message':'not your user to delete'}, 400

		transfer_user_decks(_id)
		query = "DELETE FROM user WHERE userID=%s"
		delete_from_db(query, (_id,))
		return {'message':'Successfully deleted user with id: ' + str(_id)}, 200