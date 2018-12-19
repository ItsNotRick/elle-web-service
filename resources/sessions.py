from flask import Flask, request, send_file
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug import secure_filename
from db import mysql
from db_utils import *
from utils import *
import os
from db import mysql
from db_utils import *
from utils import *
import csv

ALLOWED_EXTENSIONS = ['csv']

def allowed_file(filename):
	
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Session(Resource):

	#@jwt_required
	def get(self, _id=None):

		if not _id:
			return {'message':'Please provide the id of the deck that you wish to get sessions for'}, 400

		file_name = 'Deck_' + str(_id) + '.csv'

		query =   """SELECT card.cardID, session.sessionID, session.elapsedTime, round.roundID, round.elapsedTime, card.cardName, loggedanswers.qaFormat
		, loggedanswers.numWrongAnswers, loggedanswers.numCorrectAnswers, user.username, session.playerScore
		FROM session INNER JOIN
		round ON session.sessionID = round.sessionID INNER JOIN
		user ON user.userID = session.userID INNER JOIN
		loggedanswers ON loggedanswers.roundID = round.roundID INNER JOIN
		card ON loggedanswers.cardID = card.cardID
		WHERE card.deckID = %s
		ORDER BY card.cardID ASC;"""

		result = get_from_db(query, (_id,))

		if not result:
			return {'message':'No deck with this ID'}, 400

		filename = 'Deck_' + str(_id) + '.csv'

		if os.path.isfile('./csvs/'+filename):
			os.remove('./csvs/'+filename)

		with open(filename, mode='w') as csv_file:
			csv_writer = csv.writer(csv_file)

			headers = ['cardID', 'sessionID', 'Session elapsedTime', 'roundID', 'Round elapsedTime', 'Card Name', 'QA Format', 'Number of Time Incorrect', 'Number of Time Correct', 'Username', 'Player Score']

			csv_writer.writerow(headers)

			for item in result:
				data_row = []
				data_row.append(item[0])
				data_row.append(item[1])
				data_row.append(item[2])
				data_row.append(item[3])
				data_row.append(item[4])
				data_row.append(item[5])
				data_row.append(item[6])
				data_row.append(item[7])
				data_row.append(item[8])
				data_row.append(item[9])
				data_row.append(item[10])
				csv_writer.writerow(data_row)

		os.system('mv ' + filename + ' ./csvs/' + filename)

		if os.path.isfile('./csvs/'+filename):
			return send_file('./csvs/'+filename, mimetype='text/csv', attachment_filename=filename, as_attachment=True)
		else:
			return {'message':'File does not exist. Please create it by picking the deck in-game'}, 400

	#@jwt_required
	def post(self, _id=None):

		user_id = get_jwt_identity()

		if 'file' not in request.files:
			return {'message':'Please upload a file!'}, 400

		file = request.files['file']

		if file.filename == '':
			return {'message':'Please name your file.'}, 400

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join('./uploads',filename))

			final_list = []
			with open('./uploads/' + filename) as csvfile:
				csv_reader = csv.reader(csvfile)
				for row in csv_reader:
					final_list.append(row)
			
			if final_list:
				last_item = final_list[-1]
				player_id = int(last_item[0])
				if player_id == -1:
					player_id = 3000
				total_wrong = int(last_item[1])
				total_right = int(last_item[2])
				date = last_item[3]
				response_score = int(last_item[4])
				player_score = int(last_item[5])
				time = last_item[6]

				query = "SELECT MAX(sessionID) FROM session"
				result = get_one_from_db(query)

				maxID = check_max_id(result)

				query = "INSERT INTO session VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
				post_to_db(query, (maxID, player_id, total_wrong, total_right, date, response_score, player_score, time))

				del final_list[-2:]
				del final_list[0]

				round_count = 0
				new_round = False

				query = "SELECT MAX(roundID) FROM round"
				result = get_one_from_db(query)

				roundID = result[0][0] + 1
				query_items = []

				try:
					for item in final_list:
						if new_round:
							start_time = item[0]
							end_time = item[1]
							total_time = item[2]
							query = "INSERT INTO round VALUES (%s,%s,%s,%s,%s,%s)"
							post_to_db(query, (roundID, maxID, round_count, start_time, end_time, total_time))
							for blah in query_items:
								query = "INSERT INTO loggedanswers VALUES (%s,%s,%s,%s,%s,%s)"
								post_to_db(query, (blah[1], blah[0], roundID, blah[2], blah[3], blah[4]))
							round_count += 1
							roundID += 1
							new_round = False
							query_items = []
						elif item[0] == "ROUND DATA":
							new_round = True
						else:
							baby_list = []
							baby_list.append(item[0])
							baby_list.append(item[2])
							baby_list.append(item[3])
							baby_list.append(item[4])
							baby_list.append(item[5])

							query_items.append(baby_list)
				except:
					return {'message':'Failed to upload to DB'}, 500

				try:
					os.system('rm ./uploads/' + filename)
				except:
					pass

			return {'message':'File uploaded and removed'}

		else:
			return {'message':'Failed to upload file.'}, 400
