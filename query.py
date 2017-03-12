from __future__ import print_function
from app import db
from datetime import datetime
from rtw import *
import sys

'''def subCategoryBelongsTo(identifications):
    cursor = db.subcategories.find(identifications)
    if cursor.count() > 0:
        identifications = dict()
        identifications["_id"] = cursor[0]["category"]
        cursor = db.categories.find(identifications)
        if cursor.count() > 0:
            return cursor[0]
        return None
    return None'''

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

'''def pickRandomSubCategory(identifications):
    #cursor = mongo.db.subcategories.find(identifications)
    cursor = db.subcategories.find(identifications)
    if cursor.count() == 0:
        return None
    rand = randint(0, cursor.count() - 1)
    return cursor[rand]'''

def setUser(_id, numMatches, numVictories, gameType, theme):

    identifications = dict()
    identifications["_id"] = _id

    cursor = db.users.find(identifications)
    if cursor.count() > 0:

        increments = dict()
        increments["numMatches.total"] = numMatches
        increments["numMatches.game" + str(gameType) + ".total"] = numMatches
        increments["numMatches.game" + str(gameType) + "." + theme] = numMatches

        increments["numVictories.total"] = numVictories
        increments["numVictories.game" + str(gameType) + ".total"] = numVictories
        increments["numVictories.game" + str(gameType) + "." + theme] = numVictories

        db.users.update_one(identifications, {"$inc": increments})
        return True
    return False

def createUser(email, user, password, permission):

    identifications = dict()

    identifications["email"] = email
    identifications["user"] = user
    identifications["password"] = password
    identifications["permission"] = permission
    identifications["online"] = False
    identifications["score"] = 0

    identifications["regDate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    identifications["numMatches"] = dict()
    identifications["numMatches"]["total"] = 0
    identifications["numMatches"]["game1"] = dict()
    identifications["numMatches"]["game2"] = dict()
    identifications["numMatches"]["game3"] = dict()
    identifications["numMatches"]["game1"]["total"] = 0
    identifications["numMatches"]["game2"]["total"] = 0
    identifications["numMatches"]["game3"]["total"] = 0

    identifications["numVictories"] = dict()
    identifications["numVictories"]["total"] = 0
    identifications["numVictories"]["game1"] = dict()
    identifications["numVictories"]["game2"] = dict()
    identifications["numVictories"]["game3"] = dict()
    identifications["numVictories"]["game1"]["total"] = 0
    identifications["numVictories"]["game2"]["total"] = 0
    identifications["numVictories"]["game3"]["total"] = 0

    _id = db.users.insert_one(identifications)
    return _id.inserted_id

'''def incrementUser(identifications, updates):
    #cursor = mongo.db.users.find(identifications)
    cursor = db.users.find(identifications)
    if cursor.count() > 0:
        #mongo.db.users.update_one(identifications, {"$set": updates})
        db.users.update_one(identifications, {"$inc": updates})
        return True
    return False'''

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
    cursor = db.users.find(identifications, no_cursor_timeout=True)
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
    if identifications["gameType"] != 2 and identifications["gameType"] != 4:
        identifications["user2"] = None
        identifications["score2"] = None
        identifications["data2"] = None
        identifications["winner"] = 0
    identifications["start"] = None
    identifications["finish"] = None
    identifications["status"] = 0
    #_id = mongo.db.games.insert_one(identifications)
    _id = db.games.insert_one(identifications)

    identifications["_id"] = _id.inserted_id
    #localGames[identifications["_id"]] = identifications;

    return _id.inserted_id

def updateGame(identifications, updates):

    #_id = identifications["_id"];
    #if _id in localGames.keys():
    #	for key in updates.keys():
    #		if key in localGames[_id].keys():
    #			localGames[_id][key] = updates[key];
    #	return True;
    #return False;
    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        db.games.update_one(identifications, {"$set": updates})
        return True
    return False

def getGame(identifications):

    #_id = identifications["_id"];
    #if _id in localGames.keys():
    #	return localGames[_id];
    #return None;
    cursor = db.games.find(identifications)
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

    #for _id in localGames.keys():
    #	if localGames[_id]["status"] == 0 and localGames[_id]["gameType"] == identifications["gameType"] and not localGames[_id]["user1"] == user:
    #		return localGames[_id];
    #return None;
    identifications["status"] = 0
    identifications["user1"] = dict()
    identifications["user1"] = { "$ne": getUser({"_id": user}) }
    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        return cursor[0]
    return None

def joinGame(identifications, user):

    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        updates = dict()
        key = str()

        if cursor[0]["user1"] == None:
            key = "user1"
        elif "user2" in cursor[0].keys() and cursor[0]["user2"] == None:
            key = "user2"

        updates[key] = getUser({"_id": user})
        updates[key].pop("permission", None)
        updates[key].pop("user", None)
        updates[key].pop("online", None)
        updates[key].pop("password", None)
        updates[key].pop("email", None)

        gameType = cursor[0]["gameType"]
        theme = cursor[0]["theme"]

        for k in updates[key]["numMatches"].keys():
            if k != "total" and k != theme:
                updates[key]["numMatches"].pop(k, None)

        if theme not in updates[key]["numMatches"].keys():
            updates[key]["numMatches"][theme] = 0

        for k in updates[key]["numVictories"].keys():
            if k != "total" and k != theme:
                updates[key]["numVictories"].pop(k, None)

        if theme not in updates[key]["numVictories"].keys():
            updates[key]["numVictories"][theme] = 0

        if not updateGame(identifications, updates):
            return False

        return setUser(user, 1, 0, gameType, theme)

    return False

def isGameReady(identifications):

    #_id = identifications["_id"];
    #if _id in localGames.keys():
    #	return localGames[_id]["user1"] != None and ("user2" not in localGames[_id].keys() or localGames[_id]["user2"] != None);
    #return False;
    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        return cursor[0]["user1"] != None and ("user2" not in cursor[0].keys() or cursor[0]["user2"] != None)
    return False

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
    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        return int(cursor[0]["status"])
    return 4

def userFromGame(identifications, number):

    #_id = identifications["_id"];
    #if _id in localGames.keys():
    #	if "user" + str(number) in localGames[_id].keys():
    #		return localGames[_id]["user" + str(number)];
    #return None;
    cursor = db.games.find(identifications)
    if cursor.count() > 0:
        if "user" + str(number) in cursor[0].keys():
            return cursor[0]["user" + str(number)]
    return None

def finishGame(identifications):

    cursor = db.games.find(identifications)

    if cursor.count() > 0:

        if cursor[0]["data1"] != None and ("data2" not in cursor[0].keys() or cursor[0]["data2"] != None) and not cursor[0]["finished"]:

            updateGame(identifications, {"finished": True})
            subIdentifications = dict()
            subIdentifications["name"] = str(cursor[0]["theme"])
            if int(cursor[0]["gameType"]) == 1:
                #category = subCategoryBelongsTo(subIdentifications)
                category = getCategory(subIdentifications)
                if category == None:
                    return False
            elif int(cursor[0]["gameType"]) == 2:
                #cur = mongo.db.categories.find(subIdentifications)
                cur = db.categories.find(subIdentifications)
                if cur.count() == 0:
                    return False
                else:
                    category = cur[0]
            data1 = cursor[0]["data1"]
            gameType = int(cursor[0]["gameType"])
            updates = dict()

            if gameType == 1:
                updates["winner"] = -1
                data2 = cursor[0]["data2"]
                score1, score2 = calculateScoresAndSetFeedback(data1, data2, category["name"][0], gameType)

                if score1 > score2:
                    updates["winner"] = cursor[0]["user1"]["_id"]
                elif score1 < score2:
                    updates["winner"] = cursor[0]["user2"]["_id"]

                updates["score1"] = score1
                idUser = dict()
                idUser["_id"] = cursor[0]["user1"]["_id"]
                updateScore(idUser, score1)
                if "score2" in cursor[0].keys():
                    updates["score2"] = score2
                    idUser["_id"] = cursor[0]["user2"]["_id"]
                    updateScore(idUser, score2)

            elif gameType == 2:
                score1 = int(cursor[0]["score1"])
                idUser = dict()
                idUser["_id"] = cursor[0]["user1"]["_id"]
                updateScore(idUser, score1)

                for category in data1.keys():
                    for entity in data1[category]:

                        numVictories = 0
                        if score1 > 0:
                            numVictories = 1

                        setFeedback(entity, category, 1, numVictories, gameType)

            elif gameType == 3:
                updates["winner"] = -1
                data2 = cursor[0]["data2"]
                score1, score2 = int(cursor[0]["score1"]), int(cursor[0]["score2"])
                idUser = dict()
                idUser["_id"] = cursor[0]["user1"]["_id"]
                updateScore(idUser, score1)
                idUser = dict()
                idUser["_id"] = cursor[0]["user2"]["_id"]
                updateScore(idUser, score2)

                if score1 > score2:
                    updates["winner"] = cursor[0]["user1"]["_id"]
                elif score1 < score2:
                    updates["winner"] = cursor[0]["user2"]["_id"]

                for category in data1:
                    entity = subIdentifications["name"].split("||")[0]

                    numVictories = 0
                    if score1 > score2:
                        numVictories = 1

                    setFeedback(entity, category, 1, numVictories, gameType)

                for category in data2:
                    entity = subIdentifications["name"].split("||")[0]

                    numVictories = 0
                    if score1 < score2:
                        numVictories = 1

                    setFeedback(entity, category, 1, numVictories, gameType)

            #TO-DO
            else:
                score1 = int(cursor[0]["score1"])
                idUser = dict()
                idUser["_id"] = cursor[0]["user1"]["_id"]
                updateScore(idUser, score1)
                for i in range(cursor[0]["score2"]):
                    for entity in data1:
                        category = None#data2[i]
                        #exists, score = existsInNell(entity, category)
                        exists, score = None, 0.0
                        fbIdent, fbUpdates, fbInc = dict(), dict(), dict()
                        fbIdent["entity"] = entity
                        fbIdent["category"] = category
                        fbUpdates["score"] = score
                        fbUpdates["lazy"] = True
                        if getFeedback(fbIdent) == None:
                            fbInc["numOccurrences"] = dict()
                            fbInc["numOccurrences"]["total"] = 1
                        else:
                            fbInc["numOccurrences.total"] = 1
                            #addFeedback(fbIdent, fbInc, fbUpdates)

            finish = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updates["status"] = 1
            updates["finish"] = finish

            if not updateGame(identifications, updates):
                return False

            if gameType == 1 or gameType == 3:
                return setUser(updates["winner"], 0,1, gameType, cursor[0]["theme"])

            return True

        else:
            updates = dict()
            updates["status"] = 3
            return updateGame(identifications, updates)
    return False
