# -*- encoding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug import secure_filename
from db import mysql
from db_utils import *
from utils import *
import os

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'ogg', 'wav', 'mp3']

def allowed_file(filename):
	
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Card(Resource):

	@jwt_required
	def post(self, _id):

		card_parser = reqparse.RequestParser()
		card_parser.add_argument('cardName',
		                          type=str,
		                          required=True,
		                          )
		card_parser.add_argument('front',
		                          type=str,
		                          required=True,
		                          )
		card_parser.add_argument('back',
		                          type=str,
		                          required=True,
		                          )
		card_parser.add_argument('difficulty',
		                          type=int,
		                          required=True,
		                          )
		card_parser.add_argument('tag',
		                          type=str,
		                          required=False,
		                          )
		card_parser.add_argument('gifLocation',
		                          type=str,
		                          required=False,
		                          )
		data = card_parser.parse_args()

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
			return {'message':'not your deck to post to'}, 400

		if 'tag' in data and data['tag']:
			tag = data['tag']
		else:
			tag = None

		if 'gifLocation' in data and data['gifLocation']:
			gifLocation = data['gifLocation']
		else:
			gifLocation = None

		query = "SELECT MAX(cardID) FROM card"
		result = get_one_from_db(query)
		
		maxID = check_max_id(result)

		query = "INSERT INTO card VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

		post_to_db(query, (maxID,_id,data['cardName'],data['front'],data['back'],data['difficulty'],tag,gifLocation))
		
		delete_deck_zip(_id)

		return {'cardID':maxID}, 201
	
	@jwt_required
	def delete(self, _id):

		user_id = get_jwt_identity()

		query = "SELECT permissionGroup from user where userID = " + str(user_id)
		permission = get_from_db(query)

		if not permission:
			return {'Message':'Not a valid user'}, 400

		permission = permission[0][0]

		result, data = check_cards_db(_id)

		if not result:
			return {'message':'cannot delete non-existing card'}, 400

		query = "SELECT deckID from card where cardID = " + str(_id)
		deckID = get_from_db(query)
		deckID = deckID[0][0]

		query = "SELECT userID from deck where deckID = " + str(deckID)
		author = get_from_db(query)
		author = author[0][0]

		if not permission == 'ad' and not author == user_id:
			return {'message':'not your card to delete'}, 400

		query = "DELETE FROM card WHERE cardID=%s"
		delete_from_db(query, (_id,))
		delete_deck_zip(data[1])
		return {'message':'Successfully deleted card with id: ' + str(_id)}, 200

class CardImage(Resource):

	@jwt_required
	def post(self, _id):

		if 'file' not in request.files:
			return {'message':'Please upload a file!'}, 400

		file = request.files['file']

		if file.filename == '':
			return {'message':'Please name your file.'}, 400

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filename = get_id_file_name(str(_id), filename)
			file.save(os.path.join('./uploads',filename))

			query = "INSERT INTO images VALUES (%s, %s)"
			new_path = './Images/' + filename
			post_to_db(query, (_id, new_path))

			os.system('mv ./uploads/' + filename + ' ./Images/' + filename)

			return {'message':'Successfully uploaded an image!'}

		else:
			return {'message':'Failed to upload file.'}, 400

class CardSound(Resource):

	@jwt_required
	def post(self, _id):

		if 'file' not in request.files:
			return {'message':'Please upload a file!'}, 400

		file = request.files['file']

		if file.filename == '':
			return {'message':'Please name your file.'}, 400

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filename = get_id_file_name(str(_id), filename)
			file.save(os.path.join('./uploads',filename))

			query = "INSERT INTO audio VALUES (%s, %s)"
			new_path = './Audio/' + filename[:-4] + '.ogg'
			post_to_db(query, (_id, new_path))

			
			success = convert_audio(filename)
			if success:
				os.system('mv ./uploads/' + filename[:-4] + '.ogg' + ' ./Audio/' + filename[:-4] + '.ogg')
				os.remove('./uploads/'+filename)
				return {'message':'Successfully uploaded a sound file!'}, 201
			else:
				return {'message':'failed to convert audio'}, 400

		else:
			return {'message':'Failed to upload file.'}, 400