from __future__ import print_function
from app import mongo, db
from random import randint
import sys


# addFeedback(identifications, updates, gameType): void
# calculateScores(data1, data2, category, gameType): int, int
# askNell(entity): list
# existsInNell(entity, category): tuple(bool, float)
# getData(identifications, uniqueKey, sortCriteria, maxValues): list
# pickRandomFeedback(identifications, sortCriteria, maxValues): dict

# initial identifications: entity, category
# initial updates: score, count
def addFeedback(identifications, increments = None, updates = None):

    cursor = db.feedbacks.find(identifications);
    if cursor.count() > 0:
        if(updates != None):
            db.feedbacks.update_one(identifications, {"$set": updates});
        if(increments != None):
            db.feedbacks.update_one(identifications, {"$inc": increments});
    else:

        toInsert = dict(identifications.items());
        if(updates != None):
            toInsert.update(updates);
        if(increments != None):
            toInsert.update(increments);
        db.feedbacks.insert_one(toInsert);


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
            return True, float(o[1])
    return False, 0.0

def incrementFeedback(player1, player2, score1, score2, category, gameType):
    for entity in player1:

        identifications = dict();
        increments = dict();

        if(entity != ""):

            identifications["entity"] = entity;
            identifications["category"] = category;

            increments["numOccurrences.total"] = 1;
            increments["numOccurrences.game" + str(gameType)] = 1;

            if(score1 > score2):
                increments["numVictories.total"] = 1;
                increments["numVictories.game" + str(gameType)] = 1;

            addFeedback(identifications, increments);

    for entity in player2:

        identifications = dict();
        increments = dict();

        if(entity != ""):

            identifications["entity"] = entity;
            identifications["category"] = category;

            increments["numOccurrences.total"] = 1;
            increments["numOccurrences.game" + str(gameType)] = 1;

            if(score2 > score1):
                increments["numVictories.total"] = 1;
                increments["numVictories.game" + str(gameType)] = 1;

            addFeedback(identifications, increments);

def calculateScores(player1_original, player2_original, category):
    player1, player2 = list(player1_original), list(player2_original);
    score1, score2 = 0, 0
    for e in player1:
        if e != "":
            exists, score = existsInNell(e, category)
            identifications = dict()
            identifications["entity"] = e
            identifications["category"] = category
            updates = dict()

            updates["lazy"] = False
            if exists:
                updates["score"] = score
                if score > 0.7:
                    if e in player2:
                        score1 += 10
                        score2 += 10
                        player2.remove(e)
                    else:
                        score1 += 4
                else:
                    if e in player2:
                        score1 += 12
                        score2 += 12
                        player2.remove(e)
                    else:
                        score1 += 7
            else:
                updates["score"] = 0.0
                if e in player2:
                    score1 += 15
                    score2 += 15
                    player2.remove(e)
                else:
                    score1 += 2

            addFeedback(identifications, None, updates);

    for e in player2:
        if e != "":
            exists, score = existsInNell(e, category)
            identifications = dict()
            identifications["entity"] = e
            identifications["category"] = category
            updates = dict()
            updates["lazy"] = False
            if exists:
                updates["score"] = score
                if score > 0.7:
                    score2 += 4
                else:
                    score2 += 7
            else:
                updates["score"] = 0.0
                score2 += 2

            addFeedback(identifications, None, updates);

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
