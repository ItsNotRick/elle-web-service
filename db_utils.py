from flaskext.mysql import MySQL
from db import mysql

def get_one_from_db(query, vals=None):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query, vals) if vals else cursor.execute(query)
	#result = cursor.fetchone()
	result = []
	for row in cursor:
		result.append(list(row))
	conn.commit()
	conn.close()
	return result

def get_from_db(query, vals=None):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query, vals) if vals else cursor.execute(query)
	#result = cursor.fetchall()
	result = []
	for row in cursor:
		result.append(list(row))
	conn.commit()
	conn.close()
	return result

def post_to_db(query, vals=None):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query, vals) if vals else cursor.execute(query)
	conn.commit()
	conn.close()

def delete_from_db(query, vals=None):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query, vals) if vals else cursor.execute(query)
	conn.commit()
	conn.close()