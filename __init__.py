from flask import Flask, render_template, Response, request, send_file, send_from_directory, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager
from flaskext.mysql import MySQL

from flask_cors import CORS

from resources.users import UserRegister, UserLogin, UserLogout, Users, User, ResetPassword, ForgotPassword, ForgotCheck, ForgotReset
from resources.sessions import Session
from resources.leaderboard import Leaderboard
from resources.decks import Deck, Decks, Game_Deck
from resources.cards import Card, CardImage, CardSound
from resources.groups import Group, Groups
from db import mysql
from db_utils import *

from pathlib import Path

import os.path

app = Flask(__name__, static_folder=Path('templates/build/static'))
CORS(app)
app.config['MYSQL_DATABASE_USER'] = 'localeservice'
app.config['MYSQL_DATABASE_PASSWORD'] = 'eserv'
app.config['MYSQL_DATABASE_DB'] = 'ellelocal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']  # allow blacklisting for access tokens
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['PROPOGATE_EXCEPTIONS'] = True
app.secret_key = 'ian'
mysql.init_app(app)
api = Api(app)

jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized(self):
	resp = Response(render_template('/build/index.html'), mimetype='text/html')
	return resp

@app.errorhandler(404)
def page_not_found(e):
	resp = Response(render_template('/build/index.html'), mimetype='text/html')
	return resp

class HomePage(Resource):
	
	def get(self):
		
		resp = Response(render_template('/build/index.html'), mimetype='text/html')
		return resp

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    query = "SELECT * from tokens"
    result = get_from_db(query)

    if result and jti in result[0]:
    	return True
    else:
    	return False

api.add_resource(HomePage, '/')
api.add_resource(Users, '/users')
api.add_resource(User, '/user')
api.add_resource(Decks, '/decks', '/decks/<int:_mark>')
api.add_resource(Deck, '/deck', '/deck/<int:_id>')
api.add_resource(Game_Deck, '/deck/zip/<int:_id>')
api.add_resource(Leaderboard, '/leaderboard/<int:_id>')
api.add_resource(Session, '/session', '/session/<int:_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserRegister, '/register')
api.add_resource(Card, '/card/<int:_id>')
api.add_resource(Groups, '/groups')
api.add_resource(Group, '/group', '/group/<int:_id>')
api.add_resource(CardImage, '/card/image/<int:_id>')
api.add_resource(CardSound, '/card/sound/<int:_id>')
api.add_resource(ForgotPassword, '/forgot')
api.add_resource(ResetPassword, '/users/reset')
api.add_resource(ForgotCheck, '/forgot/check')
api.add_resource(ForgotReset, '/forgot/reset')

app.run(port=5000, debug=True)
