from __future__ import print_function
from app import db
from random import randint
import sys

def toHash(inputString):
    import hashlib
    return hashlib.sha512(inputString).hexdigest()

def setFeedback(entity, category, numOccurrences, numVictories, gameType, scoreInNell = -1):

    identifications = dict()
    identifications["entity"] = entity
    identifications["category"] = category

    if scoreInNell == -1:
        scoreInNell = existsInNell(entity, category)

    if getFeedback(identifications) == None:
        toInsert = dict(identifications.items())
        toInsert["numOccurrences"] = dict()
        toInsert["numOccurrences"]["total"] = 0
        toInsert["numVictories"] = dict()
        toInsert["numVictories"]["total"] = 0

        if gameType > 0:
            toInsert["numOccurrences"]["game" + str(gameType)] = 0
            toInsert["numOccurrences"]["game" + str(gameType)] = 0

        db.feedbacks.insert_one(toInsert)

    existingFeedback = getFeedback(identifications)
    score = scoreInNell

    '''print("-----")
    print(existingFeedback["entity"] + " - " + existingFeedback["category"])
    print(score)
    print(existingFeedback["numVictories"]["total"] + numVictories)
    print(existingFeedback["numOccurrences"]["total"] + numOccurrences)'''

    if (existingFeedback["numOccurrences"]["total"] + numOccurrences) > 0:
        score += float(existingFeedback["numVictories"]["total"] + numVictories) / \
                 (existingFeedback["numOccurrences"]["total"] + numOccurrences)

    '''print(score)
    print("-----")'''

    updates = dict()
    updates["scoreInNell"] = scoreInNell
    updates["score"] = score

    increments = dict()
    increments["numOccurrences.total"] = numOccurrences
    increments["numVictories.total"] = numVictories

    if gameType > 0:
        increments["numOccurrences.game" + str(gameType)] = numOccurrences
        increments["numVictories.game" + str(gameType)] = numVictories

    db.feedbacks.update_one(identifications, {"$set": updates, "$inc": increments})

    return scoreInNell, score

def createSeed(entity, category):
    return setFeedback(entity, category, 0, 0, 0)

def askNell(entity):
    import json
    import urllib2
    occurrences = []
    url = 'http://rtw.ml.cmu.edu/rtw/api/json0?lit1=' + entity.replace(" ", "+") + '&predicate=*'
    json_dict = json.load(urllib2.urlopen(url))
    if "items" in json_dict.keys():
        for i in json_dict["items"]:
            if "predicate" in i.keys():
                if "justifications" in i.keys() and len(i["justifications"]) >= 1 and "score" in i["justifications"][0].keys():
                    occurrences.append((i["predicate"], i["justifications"][0]["score"]))
    return occurrences

def existsInNell(entity, category):
    # communicate with ask nell, returns the list of occurrences of entity
    occurrences = askNell(entity)
    for o in occurrences:
        if str(o[0]) == category:
            return float(o[1])
    return 0.0

def calculateScoresAndSetFeedback(player1_original, player2_original, category, gameType):

    player1, player2 = list(player1_original), list(player2_original)
    score1, score2 = 0, 0
    inNell = dict()

    for entity in player1:
        if entity != "":

            inNell[entity] = existsInNell(entity, category)

            if inNell[entity] > 0.7:
                if entity in player2:
                    score1 += 10
                    score2 += 10
                    player2.remove(entity)
                else:
                    score1 += 4
            else:
                if entity in player2:
                    score1 += 12
                    score2 += 12
                    player2.remove(entity)
                else:
                    score1 += 7

    for entity in player2:
        if entity != "":

            inNell[entity] = existsInNell(entity, category)

            if inNell[entity] > 0.7:
                score2 += 4
            else:
                score2 += 7

    for entity in player1_original:
        numVictories = 0
        if score1 > score2:
            numVictories += 1

        setFeedback(entity, category, 1, numVictories, gameType, inNell[entity])

    for entity in player2_original:
        numVictories = 0
        if score1 < score2:
            numVictories += 1

        setFeedback(entity, category, 1, numVictories, gameType, inNell[entity])

    return score1, score2

def getData(identifications, sortCriteria, maxValues):
    # cursor = mongo.db.feedbacks.find(identifications).sort(sortCriteria)
    cursor = db.feedbacks.find(identifications).sort(sortCriteria)
    data = []
    if cursor.count() > 0:
        for i in range(min(maxValues, cursor.count())):
            data.append(str(cursor[i]["entity"]))
    return data

def pickRandomFeedback(identifications, sortCriteria, maxValues):
    data = getData(identifications, sortCriteria, maxValues)
    rand = randint(0, len(data) - 1)
    return data[rand]

def getFeedback(identifications):
    cursor = db.feedbacks.find(identifications, no_cursor_timeout=True)
    if cursor.count() > 0:
        return cursor[0]
    return None


