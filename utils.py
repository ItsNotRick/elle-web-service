from db import mysql
from db_utils import *
from time import sleep
import os
import shutil
import csv
import subprocess

########################################################################################
# DECKS FUNCTIONS
########################################################################################

def create_csv(data, _id):
	
	filename = 'Deck_' + _id + '.csv'
	with open(filename, mode='w') as csv_file:
		csv_writer = csv.writer(csv_file)

		headers = ['id', 'English', 'Translation']
		csv_writer.writerow(headers)

		for item in data:
			data_row = []
			data_row.append(item[0])
			data_row.append(item[3])
			data_row.append(item[4].encode('utf-8').strip())
			csv_writer.writerow(data_row)

	os.system('mv ' + filename + ' ./zips/Deck_' + _id)

def create_zip(data, _id, deck_name):
	
	file_name = './zips/Deck_' +  _id + '.zip'

	while(os.path.isdir("./zips/Deck_" + _id) and not os.path.isfile(file_name)):
		sleep(2)

	if os.path.isfile(file_name):
		return

	try:
		os.system('mkdir ./zips/Deck_' + _id)
		os.system('mkdir ./zips/Deck_' + _id + '/Audio')
		os.system('mkdir ./zips/Deck_' + _id + '/Images')
		f = open('./zips/Deck_' + _id + '/Name.txt', 'w')
		f.write(deck_name)
		f.close()
	except:
		pass

	create_csv(data, _id)

	# len(audio) == len(images)
	for item in data:
		image_name = str(item[8].split('/')[-1])
		audio_name = str(item[9].split('/')[-1])

		file_path = './zips/Deck_' + _id

		os.system('cp ./Audio/' + audio_name + ' ./zips/Deck_' + _id + '/Audio')
		os.system('cp ./Images/' + image_name + ' ./zips/Deck_' + _id + '/Images')

	shutil.make_archive('./zips/Deck_' +  _id, 'zip', './zips/Deck_' + _id)

	os.system('rm -rf ./zips/Deck_' + _id)

def get_id_file_name(_id, filename):
	
	id_length = len(_id)

	if id_length < 4:
		new_id = _id
		while(len(new_id) < 4):
			new_id = '0' + new_id

	return new_id + filename

def check_decks_db(_id):

	query = "SELECT * FROM deck WHERE deckID=%s"
	result = get_from_db(query, (_id,))

	for row in result:
		if row[0] == _id:
			return True
	
	return False

def delete_deck_zip(_id):

	file_name = './zips/Deck_' +  str(_id) + '.zip'

	if(os.path.isfile(file_name)):
		os.system('rm ' + file_name)

########################################################################################
# CARDS FUNCTIONS
########################################################################################

def check_cards_db(_id):

	query = "SELECT * FROM card WHERE cardID=%s"
	result = get_from_db(query, (_id,))

	for row in result:
		if row[0] == _id:
			return True, row
	
	return False, None

def convert_audio(filename):

	try:
		true_filename = './uploads/' + filename
		output_name = './uploads/' + filename[:-4] + '.ogg'
		command = ['ffmpeg','-i']
		command.append(true_filename)
		command.append('-c:a')
		command.append('libvorbis')
		command.append('-b:a')
		command.append('64k')
		command.append(output_name)
		output = subprocess.check_output(command)
		return True
	except Exception as e:
		return False

########################################################################################
# GROUPS FUNCTIONS
########################################################################################

def check_groups_db(_id):

	query = "SELECT * FROM grouptb WHERE groupID=%s"
	result = get_from_db(query, (_id,))

	for row in result:
		if row[0] == _id:
			return True
	
	return False

########################################################################################
# USERS FUNCTIONS
########################################################################################

def transfer_user_decks(_id):

	query = "UPDATE deck SET userID=%s WHERE userID=%s"
	post_to_db(query, (3000,_id)) # 3000 is our current admin

def put_in_blacklist(_id):

	query = "SELECT lastToken from user where userID = " + str(_id)
	result = get_from_db(query)

	if result[0][0]:
		query = "INSERT INTO tokens VALUES (%s)"
		post_to_db(query, (result[0][0],))
		query = "UPDATE user set lastToken = %s where userID = " + str(_id)
		post_to_db(query, (None,))

########################################################################################
# ALL FUNCTIONS
########################################################################################

def check_max_id(result):

	if result[0][0]:
		return result[0][0] + 1

	else:
		return 1