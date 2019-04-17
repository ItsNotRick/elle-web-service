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
		user_parser.add_argument('confirm',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('classID',
		                          type=str,
		                          required=False,
		                          )
		user_parser.add_argument('pass_question',
		                          type=int,
		                          required=True,
		                          )
		user_parser.add_argument('pass_answer',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()
		
		if data['password'] != data['confirm']:
			return{'message':'Passwords do not match!'},400

		find_user, user = find_by_name(data['username'])

		if find_user:
			return {'message':'A user with that name already exists!'}, 400

		query = "SELECT MAX(userID) FROM user"
		result = get_one_from_db(query)
		
		maxID = check_max_id(result)

		classID = data['classID'] if 'classID' in data else -1

		if data['classID'] != '':
			classID = int(data['classID'])
		else:
			classID = -1


		query = "INSERT INTO user VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

		salted_password = generate_password_hash(data['password'])
		salted_answer = generate_password_hash(data['pass_answer'])

		post_to_db(query, (maxID,data['username'],salted_password,'key','reset','us',0,None,'',0,'',0,data['pass_question'],salted_answer))
		
		if classID >= 0:
			class_query = "INSERT INTO group_user values (%s, %s,%s)"
			post_to_db(class_query,(classID,maxID,0))

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
			else:
				return {'message':'Incorrect Password!'}, 401
		return {'message':'User Not Found!'}, 401

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
		user_parser.add_argument('confirm',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()
		
		if data['pw'] != data['confirm']:
			return{'message':'Passwords do not match!'},400

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
	def get(self):
		_id = get_jwt_identity()
		query = "SELECT * FROM user WHERE userID = "+str(_id)
		result = get_from_db(query)
		for row in result:
			stuff = {}
			stuff['id'] = row[0]
			stuff['username'] = row[1]
			stuff['motivation'] = row[10]
		return stuff
		#_id = 300
		#print(_id)
		#return {'message':'Successfully reset the password'+str(_id)}, 400

class ForgotPassword(Resource):
	def post(self):
		user_parser = reqparse.RequestParser()
		user_parser.add_argument('username',
		                          type=str,
		                          required=True,
		                          )

		data = user_parser.parse_args()
		find_user, user = find_by_name(data['username'])
		if find_user:
			question = user[12]
			if question == 1:
				return{
					'question': 'What is your favorite book?'
				}, 200
			elif question == 2:
				return{
					'question': 'What is the name of the road you grew up on?'
				}, 200
			elif question == 3:
				return{
					'question': 'What is the name of your favorite pet?'
				}, 200
			elif question == 4:
				return{
					'question': 'What is your favorite food?'
				}, 200
			elif question == 5:
				return{
					'question': 'What was the model of your first car?'
				}, 200
			elif question == 0:
				return{
					'question': 'You do not have a security question. Please create a new account.'
				}, 200
			else:
				return{
					'question': "Couldn't find question"
				}, 400
		else: return{'message':"User not found"},400

class ForgotCheck(Resource):
	def post(self):
		user_parser = reqparse.RequestParser()
		user_parser.add_argument('username',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('answer',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()

		user = data['username']
		find_user, user = find_by_name(data['username'])
		if find_user:
			if check_password_hash(user[13],data['answer']):
				return {'message':'Answer matches security question',
						'userID':user[0]}, 201
			else:
				return {'message':'Incorrect Answer!'}, 400
		return {'message':'User Not Found!'}, 400


class ForgotReset(Resource):

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
		user_parser.add_argument('confirm',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()
		
		if data['pw'] != data['confirm']:
			return{'message':'Passwords do not match!'},400

		pw = generate_password_hash(data['pw'])

		query = "UPDATE user SET password=%s WHERE userID=" + str(data['userID'])

		post_to_db(query, (pw,))

		return {'message':'Successfully reset the password'}, 201
		
