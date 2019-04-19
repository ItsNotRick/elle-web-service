# -*- encoding: utf-8 -*-

from flask import send_file, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_raw_jwt
from db import mysql
from db_utils import *
from utils import *
import os.path

class Decks(Resource):

	@jwt_required
	def get(self, _mark=None):

		_id = get_jwt_identity()

		query = "UPDATE user set lastToken = %s where userID = " + str(_id)
		post_to_db(query, (get_raw_jwt()['jti'],))

		query = "SELECT permissionGroup from user where userID = " + str(_id)
		permission = get_from_db(query)

		if not permission:
			return {'Message':'Not a valid user'}, 400

		permission = permission[0][0]

		# Pull all decks
		query = "SELECT * FROM deck"
		deck_result = get_from_db(query)

		deck_ids = []
		deck_names = []
		mark_deck = []

		# Check if admin
		if permission == 'ad':
			if _mark == 49:
				for row in deck_result:
					mark_deck.append({'id':row[0],'name':row[3]})

				return mark_deck

			else: 
				for row in deck_result:
					deck_ids.append(row[0])
					deck_names.append(row[3])

				return {'ids':deck_ids,'names':deck_names}

		# Get groups the user is in
		query = "SELECT * FROM group_user WHERE userID = " + str(_id)
		user_result = get_from_db(query)

		# Gather groupIDs
		groupList = []
		for row in user_result:
			groupList.append(row[0])
		
		# Parse through decks and check if they can be returned
		for row in deck_result:
			# User created
			if row[1] == _id:
				mark_deck.append({'id':row[0],'name':row[3]})
				deck_ids.append(row[0])
				deck_names.append(row[3])
			# Public
			elif row[7] == 'pb':
				mark_deck.append({'id':row[0],'name':row[3]})
				deck_ids.append(row[0])
				deck_names.append(row[3])
			# Group deck
			elif row[2] in groupList:
				# Check status and privacy
				if row[6] == 1 and row[7] == 'gr':
					mark_deck.append({'id':row[0],'name':row[3]})
					deck_ids.append(row[0])
					deck_names.append(row[3])
		
		if _mark == 49:
			return mark_deck

		else:
			return {'ids':deck_ids,'names':deck_names}

class Deck(Resource):
	
	@jwt_required
	def get(self, _id=None):

		# Super insecure, the jwt isn't actually checked to see if 
		# this specific user should be accessing this deck.
		if not _id:
			return {'message':'Please provide the id of the deck that you wish to get'}, 400

		query = "SELECT * FROM deck WHERE deckID = " + str(_id)
		result = get_from_db(query)

		if not result:
			return {'Message':'Not a valid deck'}, 400

		query = "SELECT * FROM card WHERE deckID = " + str(_id)
		result = get_from_db(query)

		final_list = []

		for row in result:
			# Image location
			query = "SELECT imageLocation FROM images WHERE cardID = " + str(row[0])
			image_result = get_from_db(query)

			# Audio location
			query = "SELECT audioLocation FROM audio WHERE cardID = " + str(row[0])
			audio_result = get_from_db(query)

			if not image_result or not audio_result:
				continue
			else:
				row.append(image_result[0][0])
				row.append(audio_result[0][0])

			new_card = {}
			new_card['cardID'] = row[0]
			new_card['deckID'] = row[1]
			new_card['cardName'] = row[2]
			new_card['front'] = row[3]
			new_card['back'] = row[4]
			new_card['difficulty'] = row[5]
			new_card['tag'] = row[6]
			new_card['gifLocation'] = row[7]
			new_card['imageLocation'] = row[8]
			new_card['audioLocation'] = row[9]
			final_list.append(new_card)		

		return final_list

	@jwt_required
	def post(self, _id=None):

		user_id = get_jwt_identity()

		deck_parser = reqparse.RequestParser()
		deck_parser.add_argument('groupID',
		                          type=int,
		                          required=False,
		                          )
		deck_parser.add_argument('deckName',
		                          type=str,
		                          required=True,
		                          )
		deck_parser.add_argument('ttype',
		                          type=str,
		                          required=True,
		                          )
		deck_parser.add_argument('version',
		                          type=str,
		                          required=False,
		                          )
		deck_parser.add_argument('status',
		                          type=str,
		                          required=False,
		                          )
		deck_parser.add_argument('privacy',
		                          type=str,
		                          required=False,
		                          )
		data = deck_parser.parse_args()

		groupID = data['groupID'] if 'groupID' in data else None
		version = data['version'] if 'age' in data else '1.0'
		status = data['status'] if 'motivation' in data else 1

		if 'privacy' in data and data['privacy']:
			privacy = data['privacy']
		else:
			privacy = 'pb'

		query = "SELECT MAX(deckID) FROM deck"
		result = get_one_from_db(query)
		
		maxID = check_max_id(result)

		query = "INSERT INTO deck VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

		post_to_db(query, (maxID,user_id,groupID,data['deckName'],data['ttype'],version,status,privacy))
		
		return {'deckID':maxID}, 201

	@jwt_required
	def delete(self, _id=None):

		if not _id:
			return {'message':'Please provide the id of the deck that you wish to delete'}, 400

		if not check_decks_db(_id):
			return {'message':'cannot delete non-existing deck'}, 400

		user_id = get_jwt_identity()

		query = "SELECT permissionGroup from user where userID = " + str(user_id)
		permission = get_from_db(query)

		if not permission:
			return {'Message':'Not a valid user'}, 400

		permission = permission[0][0]

		query = "SELECT userID from deck where deckID = " + str(_id)
		author = get_from_db(query)
		author = author[0][0]

		if not permission == 'ad' and not author == user_id:
			return {'message':'not your deck to delete'}, 400

		query = "DELETE FROM deck WHERE deckID=%s"
		delete_from_db(query, (_id,))
		delete_deck_zip(_id)
		return {'message':'Successfully deleted deck with id: ' + str(_id)}, 200

class Game_Deck(Resource):

	@jwt_required
	def get(self, _id):
		audio_locations = []
		image_locations = []

		query = "SELECT * FROM card WHERE deckID = " + str(_id)
		result = get_from_db(query)

		if not result:
			return {'Message':'Not a valid deck'}, 400

		count = 0
		skip = []
		for row in result:
			# Image location
			query = "SELECT * FROM images WHERE cardID = " + str(row[0])
			image_result = get_from_db(query)

			# Audio location
			query = "SELECT * FROM audio WHERE cardID = " + str(row[0])
			audio_result = get_from_db(query)

			if not image_result or not audio_result:
				skip.append(count)
			else:
				row.append(image_result[0][1])
				row.append(audio_result[0][1])

			count += 1

		for item in skip:
			del result[item]

		query = "SELECT deckName FROM deck WHERE deckID = " + str(_id)
		deck_name = get_from_db(query)
		deck_name = deck_name[0][0]
		create_zip(result, str(_id), deck_name)

		file_name = 'Deck_' + str(_id) + '.zip'

		if os.path.isfile('./zips/'+file_name):
			return send_file('./zips/'+file_name, mimetype='text/csv', attachment_filename=file_name, as_attachment=True)
		else:
			return {'message':'File does not exist. Please create it by picking the deck in-game'}, 400
