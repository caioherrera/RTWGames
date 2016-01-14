from __future__ import print_function
from app import mongo
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
	cursor = mongo.db.subcategories.find(identifications)
	if cursor.count() > 0:
		identifications = dict()
		identifications["_id"] = cursor[0]["category"]
		cursor = mongo.db.categories.find(identifications)
		if cursor.count() > 0:
			return cursor[0]
		return None
	return None

def pickRandomCategory():
	cursor = mongo.db.categories.find({})
	if cursor.count() == 0:
		return None
	rand = randint(0, cursor.count() - 1)
	return cursor[rand]	

def pickRandomSubCategory(identifications):
	cursor = mongo.db.subcategories.find(identifications)
	if cursor.count() == 0:
		return None
	rand = randint(0, cursor.count() - 1)
	return cursor[rand]

def createUser(identifications):
	identifications["online"] = False
	_id = mongo.db.users.insert_one(identifications)
	return _id.inserted_id

def updateUser(identifications, updates):
	cursor = mongo.db.users.find(identifications)
	if cursor.count() > 0:
		mongo.db.users.update_one(identifications, {"$set": updates})
		return True
	return False

def getUser(identifications):
	cursor = mongo.db.users.find(identifications)
	if cursor.count() > 0:
		return cursor[0]
	return None

def isUserOnline(identifications):
	user = getUser(identifications)
	return user != None and user["online"]

def changeUserStatus(identifications, online):
	cursor = mongo.db.users.find(identifications)
	updates = dict()
	updates["online"] = online
	return updateUser(identifications, updates)

#initial identifications: gameType, theme
def createGame(identifications):
	createdTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	identifications["createdTime"] = createdTime
	identifications["user1"] = None
	identifications["data1"] = None
	identifications["score1"] = None
	identifications["data2"] = None #for game type 2, data2 will be the collection of hints
	if identifications["gameType"] != 2:
		identifications["user2"] = None
		identifications["score2"] = None
	identifications["start"] = None
	identifications["finish"] = None
	identifications["status"] = 0
	_id = mongo.db.games.insert_one(identifications)
	return _id.inserted_id

def updateGame(identifications, updates):
	cursor = mongo.db.games.find(identifications)
	if cursor.count() > 0:
		mongo.db.games.update_one(identifications, {"$set": updates})
		return True
	return False

def getGame(identifications):
	cursor = mongo.db.games.find(identifications)
	if cursor.count() > 0:
		return cursor[0]
	return None

#initial identifications: gameType
#STATUS:
#0: esperando jogador
#1: encerrado
#2: sendo jogado
#3: parcialmente encerrado
#4: jogo nao criado
def findWaitingGame(identifications, user):
	identifications["status"] = 0
	cursor = mongo.db.games.find(identifications)
	for i in range(cursor.count()):
		if cursor[i]["user1"] != user:
			return cursor[i]
	return None

def joinGame(identifications, user):
	cursor = mongo.db.games.find(identifications)
	if cursor.count() > 0:
		updates = dict()
		if cursor[0]["user1"] == None:
			updates["user1"] = user
			return updateGame(identifications, updates)
		elif "user2" in cursor[0].keys() and cursor[0]["user2"] == None:
			updates["user2"] = user
			return updateGame(identifications, updates)
		return False
	return False

def isGameReady(identifications):
    cursor = mongo.db.games.find(identifications)
    if cursor.count() > 0:
		if "user2" in cursor[0].keys():
			return cursor[0]["user1"] != None and cursor[0]["user2"] != None
		else:
			return cursor[0]["user1"] != None
    return False

def startGame(identifications):
	start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	updates = dict()
	updates["status"] = 2
	updates["start"] = start
	return updateGame(identifications, updates)   

def checkGameStatus(identifications):
	cursor = mongo.db.games.find(identifications)
	for c in cursor:
		return int(c["status"])
	return 4

def userFromGame(identifications, number):
	cursor = mongo.db.games.find(identifications)
	if cursor.count() > 0 and "user" + str(number) in cursor[0].keys():
		return cursor[0]["user" + str(number)]
	return None	

def finishGame(identifications):
	cursor = mongo.db.games.find(identifications)
	if cursor.count() > 0:
		if cursor[0]["data1"] != None and cursor[0]["data2"] != None:
			subIdentifications = dict()
			subIdentifications["name"] = str(cursor[0]["theme"])
			category = subCategoryBelongsTo(subIdentifications)
			if category == None:
				return False
			data1 = str.split(str(cursor[0]["data1"]).lower(), "||")
			data2 = str.split(str(cursor[0]["data2"]).lower(), "||")
			gameType = int(cursor[0]["gameType"])
			score1, score2 = calculateScores(data1, data2, category["name"], gameType)
			finish = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			updates = dict()
			updates["status"] = 1
			updates["finish"] = finish
			updates["score1"] = score1
			if "score2" in cursor[0].keys():
				updates["score2"] = score2
			return updateGame(identifications, updates)
		else:
			updates = dict()
			updates["status"] = 3
			return updateGame(identifications, updates)		
	return False
