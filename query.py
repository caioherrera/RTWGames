from __future__ import print_function
from app import mongo, db
from datetime import datetime
from bson.objectid import ObjectId
from random import randint
from rtw import *
import sys

#subCategoryBelongsTo(identifications): dict | None
#pickRandomCategory(): dict | None
#pickRandomSubCategory(identifications): dict | None

#createUser(identifications): ObjectId
#updateUser(identifications, updates): bool
#getUser(identifications): dict | None
#isUserOnline(identifications): bool
#changeUserStatus(identifications, online): bool
#updateScore(identifications, score): bool

#createGame(identifications): ObjectId
#updateGame(identifications, updates): bool
#getGame(identifications): dict | None
#findWaitingGame(identifications, user): dict | None
#joinGame(identifications, user): bool
#isGameReady(identifications): bool
#startGame(identifications): bool
#checkGameStatus(identifications): int
#userFromGame(identifications, number): ObjectId | None
#finishGame(identifications): bool

localGames = dict();

def createSeed(identifications):
	updates = dict();
	updates["isInNell"], updates["score"] = existsInNell(identifications["entity"], identifications["category"]);
	updates["lazy"] = False;
	updates["count"] = 1;
	addFeedback(identifications, updates, 0);		

def subCategoryBelongsTo(identifications):
	#cursor = mongo.db.subcategories.find(identifications)
	cursor = db.subcategories.find(identifications)
	if cursor.count() > 0:
		identifications = dict()
		identifications["_id"] = cursor[0]["category"]
		#cursor = mongo.db.categories.find(identifications)
		cursor = db.categories.find(identifications)
		if cursor.count() > 0:
			return cursor[0]
		return None
	return None

def getCategory(identifications):
	cursor = db.categories.find(identifications)
	if cursor.count() > 0:
		return cursor[0]
	return None

def pickRandomCategory():
	#cursor = mongo.db.categories.find({})
	cursor = db.categories.find({})
	if cursor.count() == 0:
		return None
	rand = randint(0, cursor.count() - 1)
	return cursor[rand]	

def pickRandomSubCategory(identifications):
	#cursor = mongo.db.subcategories.find(identifications)
	cursor = db.subcategories.find(identifications)
	if cursor.count() == 0:
		return None
	rand = randint(0, cursor.count() - 1)
	return cursor[rand]

def createUser(identifications):
	identifications["online"] = False
	identifications["score"] = 0
	regDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")	
	identifications["regDate"] = regDate
	#_id = mongo.db.users.insert_one(identifications)
	_id = db.users.insert_one(identifications)
	return _id.inserted_id

def updateUser(identifications, updates):
	#cursor = mongo.db.users.find(identifications)
	cursor = db.users.find(identifications)
	if cursor.count() > 0:
		#mongo.db.users.update_one(identifications, {"$set": updates})
		db.users.update_one(identifications, {"$set": updates})
		return True
	return False

def getUser(identifications):
	#cursor = mongo.db.users.find(identifications)
	cursor = db.users.find(identifications)
	if cursor.count() > 0:
		return cursor[0]
	return None

def isUserAdmin(identifications):
	user = getUser(identifications)
	return user != None and user["permission"] == 1

def isUserOnline(identifications):
	user = getUser(identifications)
	return user != None and user["online"]

def changeUserStatus(identifications, online):
	#cursor = mongo.db.users.find(identifications)
	cursor = db.users.find(identifications)
	updates = dict()
	updates["online"] = online
	return updateUser(identifications, updates)

def updateScore(identifications, score):
	#cursor = mongo.db.users.find(identifications)
	cursor = db.users.find(identifications)
	if cursor.count() == 0:
		return False
	updates = dict()
	updates["score"] = cursor[0]["score"] + score
	return updateUser(identifications, updates)

#initial identifications: gameType, theme
def createGame(identifications):
	createdTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	identifications["createdTime"] = createdTime
	identifications["finished"] = False
	identifications["user1"] = None
	identifications["data1"] = None
	identifications["score1"] = 0
	if not "data2" in identifications.keys():
		identifications["data2"] = None 			#for game type 2, data2 will be the collection of hints
	identifications["score2"] = 0 					#for game type 2, score2 will store the number of hints needed for the user to give the correct answer
	if identifications["gameType"] != 2 and identifications["gameType"] != 4:
		identifications["user2"] = None
	identifications["start"] = None
	identifications["finish"] = None
	identifications["status"] = 0
	#_id = mongo.db.games.insert_one(identifications)
	_id = db.games.insert_one(identifications)

	identifications["_id"] = _id.inserted_id;
	#localGames[identifications["_id"]] = identifications;

	return _id.inserted_id

def saveGame(identifications):
	#print("saveGame", file=sys.stderr);
	_id = identifications["_id"];
	if _id in localGames.keys():
		#print("salvando o jogo", file=sys.stderr);
		db.games.update_one({"_id": _id}, {"$set": localGames[_id]});
		return True;
	return False;

def updateGame(identifications, updates):

	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	for key in updates.keys():
	#		if key in localGames[_id].keys():
	#			localGames[_id][key] = updates[key];
	#	return True;
	#return False;	
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		db.games.update_one(identifications, {"$set": updates});
		return True;
	return False;

def getGame(identifications):

	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	return localGames[_id];
	#return None;
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		return cursor[0];
	return None;

#initial identifications: gameType
#STATUS:
#0: esperando jogador
#1: encerrado
#2: sendo jogado
#3: parcialmente encerrado
#4: jogo nao criado

def findWaitingGame(identifications, user):

	#for _id in localGames.keys():
	#	if localGames[_id]["status"] == 0 and localGames[_id]["gameType"] == identifications["gameType"] and not localGames[_id]["user1"] == user:
	#		return localGames[_id];
	#return None;
	identifications["status"] = 0;
	identifications["user1"] = { "$ne": user };
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		return cursor[0];
	return None;

def joinGame(identifications, user):

	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	updates = dict();
	#	if localGames[_id]["user1"] == None:
	#		updates["user1"] = user;
	#		return updateGame(identifications, updates);
	#	elif "user2" in localGames[_id].keys() and localGames[_id]["user2"] == None:
	#		updates["user2"] = user;
	#		return updateGame(identifications, updates);
	#return False;
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		updates = dict();
		if(cursor[0]["user1"] == None):
			updates["user1"] = user;
			return updateGame(identifications, updates);
		elif("user2" in cursor[0].keys() and cursor[0]["user2"] == None):
			updates["user2"] = user;
			return updateGame(identifications, updates);			
	return False;

def isGameReady(identifications):

	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	return localGames[_id]["user1"] != None and ("user2" not in localGames[_id].keys() or localGames[_id]["user2"] != None);
	#return False;
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		return cursor[0]["user1"] != None and ("user2" not in cursor[0].keys() or cursor[0]["user2"] != None);
	return False;

def startGame(identifications):
	start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	updates = dict()
	updates["status"] = 2
	updates["start"] = start
	return updateGame(identifications, updates)   

def checkGameStatus(identifications):
	
	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	return int(localGames[_id]["status"]);
	#return 4;
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		return int(cursor[0]["status"]);
	return 4;

def userFromGame(identifications, number):

	#_id = identifications["_id"];
	#if _id in localGames.keys():
	#	if "user" + str(number) in localGames[_id].keys():
	#		return localGames[_id]["user" + str(number)];
	#return None;	
	cursor = db.games.find(identifications);
	if(cursor.count() > 0):
		if("user" + str(number) in cursor[0].keys()):
			return cursor[0]["user" + str(number)];
	return None;

def finishGame(identifications):
	
	cursor = db.games.find(identifications)

	if(cursor.count() > 0):
		if cursor[0]["data1"] != None and cursor[0]["data2"] != None and not cursor[0]["finished"]:
			updateGame(identifications, {"finished": True})
			subIdentifications = dict()
			subIdentifications["name"] = str(cursor[0]["theme"])
			if int(cursor[0]["gameType"]) == 1:
				#category = subCategoryBelongsTo(subIdentifications)
				category = getCategory(subIdentifications);
				if category == None: 
					return False
			elif int(cursor[0]["gameType"]) == 2:
				#cur = mongo.db.categories.find(subIdentifications)
				cur = db.categories.find(subIdentifications)
				if cur.count() == 0:
					return False
				else:
					category = cur[0]
			data1 = str.split(str(cursor[0]["data1"]).lower(), "||")
			data2 = str.split(str(cursor[0]["data2"]).lower(), "||")
			gameType = int(cursor[0]["gameType"])
			updates = dict()
			if gameType == 1:
				score1, score2 = calculateScores(data1, data2, category["name"][0], 1)
				updates["score1"] = score1
				idUser = dict()
				idUser["_id"] = cursor[0]["user1"]
				updateScore(idUser, score1)
				if "score2" in cursor[0].keys():
					updates["score2"] = score2
					idUser["_id"] = cursor[0]["user2"]
					updateScore(idUser, score2)
			elif gameType == 2:
				score1 = int(cursor[0]["score1"])
				idUser = dict()
				idUser["_id"] = cursor[0]["user1"]
				updateScore(idUser, score1)
				for i in range(cursor[0]["score2"]):
					for category in data1:
						entity = data2[i]
						#exists, score = existsInNell(entity, category)
						exists, score = None, 0.0
						fbIdent = dict()
						fbUpdates = dict()
						fbIdent["entity"] = entity
						fbIdent["category"] = category
						fbUpdates["score"] = score
						fbUpdates["count"] = 1
						fbUpdates["lazy"] = True
						addFeedback(fbIdent, fbUpdates, 2)
			elif gameType == 3:
				score1, score2 = int(cursor[0]["score1"]), int(cursor[0]["score2"])
				idUser = dict()
				idUser["_id"] = cursor[0]["user1"]
				updateScore(idUser, score1)
				idUser = dict()
				idUser["_id"] = cursor[0]["user2"]
				updateScore(idUser, score2)
				for category in data1:
					entity = subIdentifications["name"].split("||")[0]					
					#exists, score = existsInNell(entity, category)
					exists, score = None, 0.0
					fbIdent, fbUpdates = dict(), dict()
					fbIdent["entity"] = entity
					fbIdent["category"] = category
					fbUpdates["score"] = score
					fbUpdates["count"] = 1
					fbUpdates["lazy"] = True
					addFeedback(fbIdent, fbUpdates, 3)
				for category in data2:
					entity = subIdentifications["name"].split("||")[1]					
					#exists, score = existsInNell(entity, category)
					exists, score = None, 0.0
					fbIdent, fbUpdates = dict(), dict()
					fbIdent["entity"] = entity
					fbIdent["category"] = category
					fbUpdates["score"] = score
					fbUpdates["count"] = 1
					fbUpdates["lazy"] = True
					addFeedback(fbIdent, fbUpdates, 3)
			else:
				score1 = int(cursor[0]["score1"])
				idUser = dict()
				idUser["_id"] = cursor[0]["user1"]
				updateScore(idUser, score1)
				for i in range(cursor[0]["score2"]):
					for entity in data1:
						category = data2[i]
						#exists, score = existsInNell(entity, category)
						exists, score = None, 0.0
						fbIdent = dict()
						fbUpdates = dict()
						fbIdent["entity"] = entity
						fbIdent["category"] = category
						fbUpdates["score"] = score
						fbUpdates["count"] = 1
						fbUpdates["lazy"] = True
						addFeedback(fbIdent, fbUpdates, 4)
			finish = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			updates["status"] = 1
			updates["finish"] = finish
			#print("finalizando o jogo", file=sys.stderr);
			return updateGame(identifications, updates);# and saveGame(identifications);
		else:
			updates = dict()
			updates["status"] = 3
			return updateGame(identifications, updates);
	return False

