from flask import request, send_file
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
from users import find_by_name
from users import check_user_db
import json
import csv
import os

class StatsInsert(Resource):
	def post(self):
		user_parser = reqparse.RequestParser()
		user_parser.add_argument('userID',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('deck_ID',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('correct',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('incorrect',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('score',
		                          type=str,
		                          required=True,
		                          )
		user_parser.add_argument('platform',
		                          type=str,
		                          required=True,
		                          )
		data = user_parser.parse_args()
		#query = "INSERT INTO gamelogs VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
		query = "INSERT INTO gamelogs (userID, deck_ID, correct, incorrect, score, platform) VALUES (%s,%s,%s,%s,%s,%s)"

		post_to_db(query,(data['userID'],data['deck_ID'],data['correct'],data['incorrect'],data['score'],data['platform']))
		return {'message':'Successfully inserted gamelog data'}, 201
		#else:
			#return {'message':'Insert failed!'}, 400

				
class Stats(Resource):
	@jwt_required
	def get(self):
		_id = get_jwt_identity()
		query = "SELECT * FROM gamelogs WHERE userID = "+str(_id)
		result = get_from_db(query)
		if not result:
			return {'message':'User not found'},400
		score_query = "SELECT MAX(score) from gamelogs WHERE userID ="+str(_id)
		score_result = get_from_db(score_query)
		
		values = []
		val1 = 0
		val2 = 0
		val3 = 0
		val4 = 0
		val5 = 0
		val6 = 0
		
		for row in result:
			if row[6] == 1 :
				val1+=1
			elif row[6] == 2 :
				val2+=1
			elif row[6] == 3 :
				val3+=1
			elif row[6] == 4 :
				val4+=1
			elif row[6] == 5 :
				val5+=1
			else:
				val6+=1
		
		values = [val1,val2,val3,val4,val5,val6]
		return {'labels': ['ELLE Mobile 2D','ELLE Mobile 3D','ELLE AR','ELLE 2.0','ELLE 1.0','Project ELLE'],
				'values': values,
				'highscore': score_result}, 200

class Progress(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        query = "SELECT * FROM gamelogs WHERE userID = "+str(user_id)
        result = get_from_db(query)
        if not result:
            return {'message':'User not found'},400
        values = []
        for row in result:
            values.append(row[5])

        return {'labels': ['Score'],
				'values': values}, 200

class BarRatio(Resource):
    #@jwt_required
    def get(self):
        user_id = get_jwt_identity()
        query = "SELECT correct, incorrect FROM gamelogs WHERE userID = "+str(user_id)
        result = get_from_db(query)
        if not result:
            return {'message':'User not found'},400
        values = []
        val1 = 0
        val2 = 0
        for row in result:
            val1 += row[0]
            val2 += row[1]
        return{'correct': val1, 'incorrect': val2}, 200

class Leaderboard(Resource):
    @jwt_required
    def get(self):
        _id = get_jwt_identity()
        query = "SELECT user.username, gamelogs.score, gamelogs.platform FROM gamelogs INNER JOIN user ON user.userID = gamelogs.userID ORDER BY score DESC LIMIT 50"
        #query = "SELECT * FROM gamelogs INNER JOIN user ON user.userID = gamelogs.userID ORDER BY score DESC LIMIT 50"

        result = get_from_db(query)
        if not result:
            	return {'message':'Leaderboard Query Unsuccessful'},400
        values = []
		
        for row in result:
            new_item = {}
            new_item['username'] = row[0] 
            new_item['score'] = row[1]
            if row[2] == 1:
                new_item['platform'] = "ELLE 2.0"
            if row[2] == 2:
                new_item['platform'] = "ELLE 2D Mobile"
            if row[2] == 3:
                new_item['platform'] = "ELLE 3D Mobile"
            if row[2] == 4:
                new_item['platform'] = "ELLE AR"
            if row[2] == 5:
                new_item['platform'] = "Project ELLE"
            else:
                new_item['platform'] = "Other Game Mode"
            values.append(new_item)
        return {'values': values}, 200
		
class ExportGameLog(Resource):
    #@jwt_required
    def get(self):
        
        #query = "SELECT gamelogs.deck_ID, deck.deckName, gamelogs.correct, gamelogs.incorrect, gamelogs.platform from gamelogs INNER JOIN deck on gamelogs.deck_ID = deck.deckID"
        query = "SELECT * from gamelogs"
        result = get_from_db(query)

        filename = 'gamelogs.csv'

        if os.path.isfile('./csvs/'+filename):
        	os.remove('./csvs/'+filename)

        if not result:
            	return {'message':'Export Query Unsuccessful'},400
        
        with open(filename, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file)
            headers = ['Deck ID', 'Deck Name', 'Correct', 'Incorrect', 'Platform']
            csv_writer.writerow(headers)
            for row in result:
                new_item = []
                new_item.append(row[0])
                new_item.append(row[1])
                new_item.append(row[2])
                new_item.append(row[3])
                if row[4] == 1:
                    new_item.append("ELLE 2.0") 
                elif row[4] == 2:
                    new_item.append("ELLE 2D Mobile")
                    #new_item['platform'] = "ELLE 2D Mobile"
                elif row[4] == 3:
                    new_item.append("ELLE 3D Mobile")
                    #new_item['platform'] = "ELLE 3D Mobile"
                elif row[4] == 4:
                    new_item.append("ELLE AR")
                    #new_item['platform'] = "ELLE AR"
                elif row[4] == 5:
                    new_item.append("Project ELLE")
                else:
                    new_item.append("Other Game Mode")
                csv_writer.writerow(new_item)
            #csv_writer.writerow("new_item")
                    #new_item['platform'] = "Project ELLE"
                #values.append(new_item)
            #csv_writer.writerow(headers)

        #return {'values': values}, 200
        os.system('mv ' + filename + ' ./csvs/' + filename)

        if os.path.isfile('./csvs/'+filename):
            return send_file('./csvs/'+filename, mimetype='text/csv', attachment_filename=filename, as_attachment=True)
        else:
            return {'message':'File does not exist. Please create it by picking the deck in-game'}, 400


