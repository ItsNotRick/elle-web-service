from flask_restful import Resource
from flask_jwt_extended import jwt_required
from db import mysql
from db_utils import *
from utils import *

class Leaderboard(Resource):

	@jwt_required
	def get(self, _id):

		query = """SELECT user.username, session.playerScore, session.elapsedTime
					FROM session INNER JOIN
				    round ON session.sessionID = round.sessionID INNER JOIN
				    user ON user.userID = session.userID INNER JOIN
				    loggedanswers ON loggedanswers.roundID = round.roundID INNER JOIN
				    card ON loggedanswers.cardID = card.cardID
			        WHERE card.deckID = %s
		            GROUP BY session.sessionID ORDER BY session.playerScore DESC"""

		result = get_from_db(query, (_id,))

		if len(result) > 10:
			result = result[:10]

		if result:
			usernames = []
			scores = []
			timeElapsed = []
			for item in result:
				usernames.append(item[0])
				scores.append(item[1])
				timeElapsed.append(item[2])
			return {'username':usernames, 'scores':scores, 'timeElapsed':timeElapsed}
		else:
			return {'message':'No scores for leaderboard'}, 400
