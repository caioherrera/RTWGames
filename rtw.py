from __future__ import print_function
from app import mongo
from random import randint
import sys

#addFeedback(identifications, updates, gameType): void
#calculateScores(data1, data2, category, gameType): int, int
#askNell(entity): list
#existsInNell(entity, category): tuple(bool, float)
#generateData(identifications, uniqueKey, sortCriteria, maxValues): list
#pickRandomFeedback(identifications, sortCriteria, maxValues): dict

#initial identifications: entity, category
#initial updates: score, count
def addFeedback(identifications, updates, gameType):
	updates["isInNell"] = (updates["score"] != -1)
	cursor = mongo.db.feedbacks.find(identifications)
	if cursor.count() > 0:
		updates["count"] += cursor[0]["count"]
		mongo.db.feedbacks.update_one(identifications, {"$set": updates})
	else:
		updates["gameType"] = gameType
		mongo.db.feedbacks.insert_one(dict(identifications.items() + updates.items()))

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
	#communicate with ask nell, returns the list of occurrences of entity
	occurrences = askNell(entity)
	for o in occurrences:
		if str(o[0]) == category:
			return True, float(o[1])
	return False, -1

def calculateScores(player1, player2, category, gameType):
	if gameType == 1:
		score1, score2 = 0, 0
		for e in player1:
			exists, score = existsInNell(e, category)
			identifications = dict()
			identifications["entity"] = e
			identifications["category"] = category
			updates = dict()
			if exists:
				updates["score"] = score
				if score > 0.7:
					if e in player2:
						updates["count"] = 2
						score1 += 10
						score2 += 10
						player2.remove(e)
					else:
						updates["count"] = 1
						score1 += 4
				else:
					if e in player2:
						updates["count"] = 2
						score1 += 12
						score2 += 12
						player2.remove(e)
					else:
						updates["count"] = 1
						score1 += 7
			else:
				updates["score"] = -1
				if e in player2:
					updates["count"] = 2
					score1 += 15
					score2 += 15
					player2.remove(e)
				else:
					updates["count"] = 1
					score1 += 2
			addFeedback(identifications, updates)
	
		for e in player2:
			exists, score = existsInNell(e, category)
			identifications = dict()
			identifications["entity"] = e
			identifications["category"] = category
			updates = dict()
			updates["count"] = 1
			if exists:
				updates["score"] = score
				if score > 0.7:
					score2 += 4
				else:
					score2 += 7
			else:
				updates["score"] = -1
				score2 += 2
			addFeedback(identifications, updates)
	
		return score1, score2
	return -1, -1

def generateData(identifications, sortCriteria, maxValues):
	cursor = mongo.db.feedbacks.find(identifications).sort(sortCriteria)
	data = []
	if cursor.count() > 0:
		for i in range(min(maxValues, cursor.count())): 
			data.append(str(cursor[i]["entity"]))
	return data

def pickRandomFeedback(identifications, sortCriteria, maxValues):
	data = generateData(identifications, sortCriteria, maxValues)
	rand = randint(0, len(data) - 1)
	return data[rand]
