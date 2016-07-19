from __future__ import print_function
from app import mongo, db
from datetime import datetime
from bson.objectid import ObjectId
from random import randint
from rtw import *
import sys

games = dict();


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
	games[_id.inserted_id] = identifications;
	return _id.inserted_id

def updateGame(identifications, updates):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		for key in updates.keys():
			games[identifications["_id"]][key] = updates[key];
		return True;
	return False;

def getGame(identifications):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		return games[identifications["_id"]];
	return None;

#initial identifications: gameType
#STATUS:
#0: esperando jogador
#1: encerrado
#2: sendo jogado
#3: parcialmente encerrado
#4: jogo nao criado
def findWaitingGame(identifications, user):
	waitingGame = None;
	for gameID in games.keys():
		if games[gameID]["status"] == 0 and games[gameID]["gameType"] == identifications["gameType"]:
			waitingGame = games[gameID];			
			break;
	return waitingGame;

def joinGame(identifications, user):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		updates = dict();
		if games[identifications["_id"]]["user1"] == None:
			updates["user1"] = user;
			return updateGame(identifications, updates);
		elif "user2" in games[identifications["_id"]].keys() and games[identifications["_id"]]["user2"] == None:
			updates["user2"] = user;
			return updateGame(identifications, updates);
	return False;

def isGameReady(identifications):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		if "user2" in games[identifications["_id"]].keys():
			return games[identifications["_id"]]["user1"] != None and games[identifications["_id"]]["user2"] != None;
		else:
			return games[identifications["_id"]]["user1"] != None;
	return False;

def startGame(identifications):
	start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	updates = dict()
	updates["status"] = 2
	updates["start"] = start
	return updateGame(identifications, updates)   

def checkGameStatus(identifications):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		return games[identifications["_id"]]["status"];
	return 4;

def userFromGame(identifications, number):

	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		if "user" + str(number) in games[identifications["_id"]].keys():
			return games[identifications["_id"]]["user" + str(number)];
	return None; 

def saveGame(identifications):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		selectedGame = games[identifications["_id"]];
		db.games.update_one({"_id": identifications["_id"]},{"$set": selectedGame});
		return True;
	return False;

def finishGame(identifications):
	if "_id" in identifications.keys() and identifications["_id"] in games.keys():
		selectedGame = games[identifications["_id"]];
		if selectedGame["data1"] != None and selectedGame["data2"] != None and not selectedGame["finished"]:
			updateGame(identifications, {"finished": True});
			subIdentifications = dict()
			subIdentifications["name"] = str(selectedGame["theme"])
			if int(selectedGame["gameType"]) == 1:
				category = subCategoryBelongsTo(subIdentifications)
				if category == None: 
					return False
			elif int(selectedGame["gameType"]) == 2:
				cur = db.categories.find(subIdentifications);
				if cur.count() == 0:
					return False;
				else:
					category = cur[0];
			data1 = str.split(str(selectedGame["data1"]).lower(), "||");
			data2 = str.split(str(selectedGame["data2"]).lower(), "||");
			gameType = int(selectedGame["gameType"]);
			updates = dict();
			
			if gameType == 1:
				score1, score2 = calculateScores(data1, data2, category["name"], 1);
				updates["score1"] = score1;
				idUser = dict();
				idUser["_id"] = selectedGame["user1"];
				updateScore(idUser, score1);
				if "score2" in selectedGame.keys():
					updates["score2"] = score2;
					idUser["_id"] = selectedGame["user2"];
					updateScore(idUser, score2);

			elif gameType == 2:
				score1 = int(selectedGame["score1"]);
				idUser = dict();
				idUser["_id"] = selectedGame["user1"];
				updateScore(idUser, score1);
				for i in range(selectedGame["score2"]):
					for category in data1:
						entity = data2[i];
						#exists, score = existsInNell(entity, category)
						exists, score = None, -1;
						fbIdent = dict();
						fbUpdates = dict();
						fbIdent["entity"] = entity;
						fbIdent["category"] = category;
						fbUpdates["score"] = score;
						fbUpdates["count"] = 1;
						fbUpdates["lazy"] = True;
						addFeedback(fbIdent, fbUpdates, 2);
			elif gameType == 3:
				score1, score2 = int(selectedGame["score1"]), int(selectedGame["score2"]);
				idUser = dict();
				idUser["_id"] = selectedGame["user1"];
				updateScore(idUser, score1);
				idUser = dict();
				idUser["_id"] = selectedGame["user2"];
				updateScore(idUser, score2);
				for category in data1:
					entity = subIdentifications["name"].split("||")[0];
					#exists, score = existsInNell(entity, category)
					exists, score = None, -1;
					fbIdent, fbUpdates = dict(), dict();
					fbIdent["entity"] = entity;
					fbIdent["category"] = category;
					fbUpdates["score"] = score;
					fbUpdates["count"] = 1;
					fbUpdates["lazy"] = True;
					addFeedback(fbIdent, fbUpdates, 3);
				for category in data2:
					entity = subIdentifications["name"].split("||")[1];
					#exists, score = existsInNell(entity, category)
					exists, score = None, -1;
					fbIdent, fbUpdates = dict(), dict();
					fbIdent["entity"] = entity;
					fbIdent["category"] = category;
					fbUpdates["score"] = score;
					fbUpdates["count"] = 1;
					fbUpdates["lazy"] = True;
					addFeedback(fbIdent, fbUpdates, 3);
			else:
				score1 = int(selectedGame["score1"]);
				idUser = dict();
				idUser["_id"] = selectedGame["user1"];
				updateScore(idUser, score1);
				for i in range(selectedGame["score2"]):
					for entity in data1:
						category = data2[i];
						#exists, score = existsInNell(entity, category)
						exists, score = None, -1;
						fbIdent = dict();
						fbUpdates = dict();
						fbIdent["entity"] = entity;
						fbIdent["category"] = category;
						fbUpdates["score"] = score;
						fbUpdates["count"] = 1;
						fbUpdates["lazy"] = True;
						addFeedback(fbIdent, fbUpdates, 4);
			finish = datetime.now().strftime('%Y-%m-%d %H:%M:%S');
			updates["status"] = 1;
			updates["finish"] = finish;
			return updateGame(identifications, updates) and saveGame(identifications);
		else:
			updates = dict();
			updates["status"] = 3;
			return updateGame(identifications, updates) and saveGame(identifications);
	return False;

