from __future__ import print_function
from flask import Flask, request, render_template, url_for, redirect, session
from app import app, mongo, db
from random import randint
from bson.objectid import ObjectId
from query import *
from rtw import *
import sys

#################################### INDEX ####################################
@app.route("/")
@app.route("/index")
def index():
    if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		if isUserOnline(identifications):
			return render_template("index.html", code = 1, username = session["user"])
		else:
			return redirect(url_for("login"))
    else:
	    return render_template("index.html", code = 0)

#################################### PROFILE ####################################
@app.route("/profile")
def profile():
    if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		if isUserOnline(identifications):
			user = getUser(identifications)
			return render_template("profile.html", _id = user["_id"], username = user["user"], email = user["email"], score = user["score"], regDate = user["regDate"])
		else:
			return redirect(url_for("login"))
    else:
	    return redirect(url_for("login"))

#################################### LOGIN ####################################
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", code = 0)
    elif request.method == "POST":
		identifications = dict()
		identifications["email"] = request.form["email"]
		identifications["password"] = request.form["password"]
		user = getUser(identifications)
		if user != None:
			changeUserStatus(identifications, True)		
			session["user"] = user["user"]
			return render_template("login.html", code = 1, username = user["user"])
		else:
			return render_template("login.html", code = 2)


#################################### REGISTER ####################################
@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html", code = 0)
	elif request.method == "POST":
		identifications = dict()
		identifications["email"] = request.form["email"]
		identifications["user"] = request.form["user"]
		identifications["password"] = request.form["password"]
		confPassword = request.form["confPassword"]
		if not identifications["password"] == confPassword:
			return render_template("register.html", code = 2)
		elif(getUser({"user": request.form["user"]}) != None): 
			return render_template("register.html", code = 3)
		elif(getUser({"email": request.form["email"]}) != None): 
			return render_template("register.html", code = 4)
		else:
			if(createUser(identifications) != None):
				return render_template("register.html", code = 1)            
			else:
				return render_template("register.html", code = 5)
	else:
		return "Invalid request"


#################################### OVERVIEW ####################################
@app.route("/overview")
def overview():
    if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		if isUserOnline(identifications):
			return render_template("overview.html", code = 1, username = session["user"])
		else:
			return redirect(url_for("login"))
    else:
	    return render_template("overview.html", code = 0)


#################################### PEOPLE ####################################
@app.route("/people")
def people():
    if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		if isUserOnline(identifications):
			return render_template("people.html", code = 1, username = session["user"])
		else:
			return redirect(url_for("login"))
    else:
	    return render_template("people.html", code = 0)


#################################### LOGOUT ####################################
@app.route("/logout")
def logout():
	identifications = dict()
	identifications["user"] = session["user"]
	changeUserStatus(identifications, False)
	session.pop("user", None)
	return render_template("logout.html")


#################################### GAMES ####################################
@app.route("/games")
def games():
	if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		if isUserOnline(identifications):
			return render_template("games.html", username = session["user"])
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))     


#################################### FIRST GAME ####################################
@app.route("/firstGame")
@app.route("/firstGame/<game>")
def firstGame(game = None):
	if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		user = getUser(identifications)
		if user != None:
			if game == None:
				identifications = dict()
				identifications["gameType"] = 1
				game = findWaitingGame(identifications, user["_id"])
				if game == None:
					category = pickRandomCategory()
					identifications = dict()
					identifications["category"] = category["_id"]
					subCategory = pickRandomSubCategory(identifications)
					theme = subCategory["name"]
					identifications = dict()
					identifications["gameType"] = 1
					identifications["theme"] = theme
					game = createGame(identifications)
					identifications["_id"] = game
					joinGame(identifications, user["_id"])
					return render_template("firstGame.html", username = user["user"], code = 0, theme = theme, game = str(game), _id = str(user["_id"]))
				else:
					identifications = dict()
					identifications["_id"] = game["_id"]
					joinGame(identifications, user["_id"])
					theme = game["theme"]
					if isGameReady(identifications):		
						startGame(identifications)
						return render_template("firstGame.html", username = user["user"], code = 2, theme = theme, game = str(game["_id"]), _id = str(user["_id"]))
					else:
						return render_template("firstGame.html", username = user["user"], code = 0, theme = theme, game = str(game["_id"]), _id = str(user["_id"]))
			else:
				idGame = -1
				theme = ""
				status = 4
				if len(game) != 24:
					return render_template("firstGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
				identifications = dict()
				identifications["_id"] = ObjectId(game)
				game = getGame(identifications)
				if game != None:
					theme = game["theme"]
					status = game["status"]
					idGame = game["_id"]
				if status == 1:
					if user["_id"] == userFromGame(identifications, 1):
						return render_template("firstGame.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score1"]))
					elif user["_id"] == userFromGame(identifications, 2):
						return render_template("firstGame.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score2"]))
					else:
						return render_template("firstGame.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
				else:
					if user["_id"] == userFromGame(identifications, 1) or user["_id"] == userFromGame(identifications, 2):
						return render_template("firstGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
					else:
						return render_template("firstGame.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))


#################################### SECOND GAME ####################################
@app.route("/secondGame")
@app.route("/secondGame/<game>")
def secondGame(game = None):
	if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		user = getUser(identifications)
		if user != None:
			if game == None:
				identifications = dict()
				category = pickRandomCategory()
				theme = category["name"]
				identifications["gameType"] = 2
				identifications["theme"] = theme
				game = createGame(identifications)
				identifications = dict()
				identifications["_id"] = game
				joinGame(identifications, user["_id"])

				dataId = dict()
				dataId["category"] = theme

				#ascending order from score
				sortCriteria = [("score", 1)]
				maxValues = 10

				data2 = str()
				first = True				
				for i in generateData(dataId, sortCriteria, maxValues):
					if not first:
						data2 += "||"
					first = False
					data2 += str(i)

				updates = dict()
				updates["data2"] = data2
				updateGame(identifications, updates)
				startGame(identifications)
				return render_template("secondGame.html", username = user["user"], code = 2, theme = theme, game = str(game), _id = str(user["_id"]), data = data2)
			else:
				idGame = -1
				theme = ""
				status = 4
				if len(game) != 24:
					return render_template("secondGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
				identifications = dict()
				identifications["_id"] = ObjectId(game)
				game = getGame(identifications)
				if game != None:
					theme = game["theme"]
					status = game["status"]
					idGame = game["_id"]
				if status == 1:
					if user["_id"] == userFromGame(identifications, 1):
						return render_template("secondGame.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score1"]))
					else:
						return render_template("secondGame.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
				else:
					return render_template("secondGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))

#################################### THIRD GAME A ####################################
@app.route("/thirdGameA")
@app.route("/thirdGameA/<game>")
def thirdGameA(game = None):
	if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		user = getUser(identifications)
		if user != None:
			if game == None:
				identifications = dict()
				identifications["gameType"] = 3
				game = findWaitingGame(identifications, user["_id"])
				if game == None:
		
					category = pickRandomCategory()
					dataId = dict()
					dataId["category"] = category["name"]
					sortCriteria = [("score", 1)]
					maxValues = 10
					theme1 = pickRandomFeedback(dataId, sortCriteria, maxValues)
					theme2 = theme1
					while theme2 == theme1:
						theme2 = pickRandomFeedback(dataId, sortCriteria, maxValues)
					identifications["theme"] = "||".join((theme1, theme2))
					game = createGame(identifications)
					identifications["_id"] = game
					joinGame(identifications, user["_id"])

					return render_template("thirdGameA.html", username = user["user"], code = 0, theme = theme1, game = str(game), _id = str(user["_id"]))

				else:
					identifications = dict()
					identifications["_id"] = game["_id"]
					joinGame(identifications, user["_id"])
					if isGameReady(identifications):		
						theme = game["theme"].split("||")[1]
						startGame(identifications)
						return render_template("thirdGameA.html", username = user["user"], code = 2, theme = theme, game = str(game["_id"]), _id = str(user["_id"]))
					else:
						theme = game["theme"].split("||")[0]
						return render_template("thirdGameA.html", username = user["user"], code = 0, theme = theme, game = str(game["_id"]), _id = str(user["_id"]))
			else:
				idGame = -1
				theme = ""
				status = 4
				if len(game) != 24:
					return render_template("thirdGameA.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
				identifications = dict()
				identifications["_id"] = ObjectId(game)
				game = getGame(identifications)
				if game != None:
					theme = game["theme"]
					status = game["status"]
					idGame = game["_id"]
				if status == 1:
					if user["_id"] == userFromGame(identifications, 1):
						return render_template("thirdGameA.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score1"]))
					elif user["_id"] == userFromGame(identifications, 2):
						return render_template("thirdGameA.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score2"]))
					else:
						return render_template("thirdGameA.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
				else:
					if user["_id"] == userFromGame(identifications, 1):
						return render_template("thirdGameA.html", username = user["user"], code = status, theme = theme.split("||")[0], game = idGame, _id = str(user["_id"]))
					elif user["_id"] == userFromGame(identifications, 2):
						if status == 3:
							return render_template("thirdGameA.html", username = user["user"], code = status, theme = theme.split("||")[1], game = idGame, _id = str(user["_id"]), data = game["data1"])
						else: return render_template("thirdGameA.html", username = user["user"], code = status, theme = theme.split("||")[1], game = idGame, _id = str(user["_id"]))
					else:
						return render_template("thirdGameA.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))


#################################### THIRD GAME B ####################################
@app.route("/thirdGameB")
@app.route("/thirdGameB/<game>")
def thirdGameB(game = None):
	if session.get("user"):
		identifications = dict()
		identifications["user"] = session["user"]
		user = getUser(identifications)
		if user != None:
			if game == None:
				return redirect(url_for("games"))
			else:
				idGame = -1
				theme = ""
				status = 4
				if len(game) != 24:
					return render_template("secondGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
				identifications = dict()
				identifications["_id"] = ObjectId(game)
				identifications["gameType"] = 3
				game = getGame(identifications)
				if game != None:
					if user["_id"] == userFromGame(identifications, 1):
						data = game["data2"]
						theme = game["theme"].split("||")[1]
					elif user["_id"] == userFromGame(identifications, 2):
						data = game["data1"]
						theme = game["theme"].split("||")[0]
					else:
						return render_template("thirdGameB.html", username = user["user"], code = 7, theme = theme, game = idGame, _id = str(user["_id"]))
					identifications = dict()
					identifications["gameType"] = 4					
					identifications["theme"] = theme
					idGame = createGame(identifications)
					identifications["_id"] = idGame
					joinGame(identifications, user["_id"])
					identifications = dict()
					identifications["_id"] = idGame
					startGame(identifications)
					updates = dict()
					updates["data2"] = data
					updateGame(identifications, updates)
					return render_template("thirdGameB.html", username = user["user"], code = 2, theme = theme, game = idGame, _id = str(user["_id"]), data = data)
				else:
					return render_template("thirdGameB.html", username = user["user"], code = 4, theme = theme, game = idGame, _id = str(user["_id"]))
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))

#################################### ENDGAME ####################################
@app.route("/endGame", methods = ["POST"])
def endGame():
	number = int(request.form["number"])
	user = ObjectId(request.form["user"])
	identifications = dict()
	identifications["_id"] = ObjectId(request.form["game"])
	updates = dict()
	if number == 1:
		if userFromGame(identifications, 1) == user:
			updates["data1"] = str(request.form["data"]).encode("UTF-8")
		else:
			updates["data2"] = str(request.form["data"]).encode("UTF-8")
	elif number == 2:
		updates["data1"] = str(request.form["data1"]).encode("UTF-8")
		updates["data2"] = str(request.form["data2"]).encode("UTF-8")
		updates["score1"] = int(request.form["score"])
		updates["score2"] = int(request.form["count"])
	elif number == 3:
		if userFromGame(identifications, 1) == user:
			updates["data1"] = str(request.form["data"]).encode("UTF-8")		
			updates["score1"] = 10
		else:
			updates["data2"] = str(request.form["data"]).encode("UTF-8")
			updates["score2"] = 10
	else:
		updates["data1"] = str(request.form["data1"]).encode("UTF-8")
		updates["data2"] = str(request.form["data2"]).encode("UTF-8")
		updates["score1"] = int(request.form["score"])
		updates["score2"] = int(request.form["count"])

	updateGame(identifications, updates)
	finishGame(identifications)
	if number == 1:
		return redirect(url_for("firstGame", game = str(identifications["_id"])))
	elif number == 2:
		return redirect(url_for("secondGame", game = str(identifications["_id"])))
	elif number == 3: 
		return redirect(url_for("thirdGameA", game = str(identifications["_id"])))
	else:
		#return redirect(url_for("thirdGameB", game = str(identifications["_id"]))
		identifications = dict()
		identifications["_id"] = user
		user = getUser(identifications)
		return render_template("thirdGameB.html", username = user["user"], code = 1, score = updates["score1"], game = str(identifications["_id"]), _id = user["_id"])


#################################### UPDATE ####################################
@app.route("/update")
def update():

	db.feedbacks.remove({})
	db.games.remove({})
	db.subcategories.remove({})
	db.categories.remove({})
	db.users.remove({})
	db.feedbacks.remove({})
	session.clear()

	db.categories.insert_one({"name": "book"})
	cursor = db.categories.find({"name": "book"})
	db.subcategories.insert_one({"name": "Sci-fi books", "category": cursor[0]["_id"]})
	db.subcategories.insert_one({"name": "Self-help books", "category": cursor[0]["_id"]})
	
	db.categories.insert_one({"name": "movie"})
	cursor = db.categories.find({"name": "movie"})
	db.subcategories.insert_one({"name": "Action movies", "category": cursor[0]["_id"]})
	db.subcategories.insert_one({"name": "Comedy movies", "category": cursor[0]["_id"]})

	db.categories.insert_one({"name": "musicsong"})
	cursor = db.categories.find({"name": "musicsong"})
	db.subcategories.insert_one({"name": "Heavy Metal musics", "category": cursor[0]["_id"]})
	db.subcategories.insert_one({"name": "Rock musics", "category": cursor[0]["_id"]})


	'''mongo.db.feedbacks.remove({})
	mongo.db.games.remove({})
	mongo.db.subcategories.remove({})
	mongo.db.categories.remove({})
	mongo.db.users.remove({})
	mongo.db.feedbacks.remove({})
	session.clear()

	mongo.db.categories.insert_one({"name": "book"})
	cursor = mongo.db.categories.find({"name": "book"})
	mongo.db.subcategories.insert_one({"name": "Sci-fi books", "category": cursor[0]["_id"]})
	mongo.db.subcategories.insert_one({"name": "Self-help books", "category": cursor[0]["_id"]})
	
	mongo.db.categories.insert_one({"name": "movie"})
	cursor = mongo.db.categories.find({"name": "movie"})
	mongo.db.subcategories.insert_one({"name": "Action movies", "category": cursor[0]["_id"]})
	mongo.db.subcategories.insert_one({"name": "Comedy movies", "category": cursor[0]["_id"]})

	mongo.db.categories.insert_one({"name": "musicsong"})
	cursor = mongo.db.categories.find({"name": "musicsong"})
	mongo.db.subcategories.insert_one({"name": "Heavy Metal musics", "category": cursor[0]["_id"]})
	mongo.db.subcategories.insert_one({"name": "Rock musics", "category": cursor[0]["_id"]})'''

	#mongo.db.games.remove({"gameType": 3})
	#mongo.db.games.remove({"gameType": 4})
	#mongo.db.feedbacks.remove({"category": "movie"})

	#cursor = mongo.db.categories.find({})
	cursor = db.categories.find({})
	string = str()
	for category in cursor:
		string += category["name"] + ": "
		#cursor2 = mongo.db.subcategories.find({"category": category["_id"]})
		cursor2 = db.subcategories.find({"category": category["_id"]})
		for subcategory in cursor2:
			string += "<li>" + subcategory["name"] + "</li>"
		string += "<br>"
	string += "<hr>"

	#cursor = mongo.db.feedbacks.find()
	cursor = db.feedbacks.find()
	string = str()
	for c in cursor:
		string += "<p>Entity: " + c["entity"] + "<br>"
		string += "Category: " + c["category"] + "<br>"
		string += "Count: " + str(c["count"]) + "<br>"
		string += "IsInNell: " + str(c["isInNell"]) + "<br>"
		string += "Score: " + str(c["score"]) + "<br>"
		string += "Lazy: " + str(c["lazy"]) + "</p>"

	return string

#################################### LAZY ####################################
@app.route("/lazy")
def lazy():
	#cursor = mongo.db.feedbacks.find({"lazy": True})
	cursor = db.feedbacks.find({"lazy": True})
	i = cursor.count()
	for c in cursor:
		identifications = dict()
		identifications["_id"] = c["_id"]
		updates = dict()
		updates["lazy"] = False
		exists, score = existsInNell(c["entity"], c["category"])
		if not exists:
			score = -1
		updates["isInNell"] = exists
		updates["score"] = score
		#mongo.db.feedbacks.update_one(identifications, {"$set": updates})
		db.feedbacks.update_one(identifications, {"$set": updates})

	return str(i) + " registers updated."

#################################### DATA ####################################
@app.route("/data", methods=["GET", "POST"])
def data():
       #gameType = 0 (all), 1, 2, 3, 4
       #position = 0 (all), 1 (entity), 2 (category)
    if session.get("user"):
               identifications = dict()
               identifications["user"] = session["user"]
               if isUserOnline(identifications):
                       user = getUser(identifications)

                       #CODE HERE
                       if request.method == "POST":
                               search = request.form["search"];
                               gameType = request.form["gameType"];
                               position = request.form["position"];
                               retorno = list();
                               identifications = dict();
                               if int(gameType) != 0:
                                       identifications["gameType"] = int(gameType);
                               if int(position) in [0, 1]:
                                       if len(search) > 0:
                                               identifications["entity"] = search;
                                       cursor = db.feedbacks.find(identifications);
                                       for item in cursor:
                                               retorno.append(item);
                               identifications = dict();
                               if int(gameType) != 0:
                                       identifications["gameType"] = int(gameType);
                               if int(position) in [0, 2]:
                                       if len(search) > 0:
                                               identifications["category"] = search;
                                               cursor = db.feedbacks.find(identifications);
                                               for item in cursor:
                                                       retorno.append(item);
                               return render_template("data.html", _id = user["_id"], username = user["user"], status = 1, data = retorno);
                       else:
                               return render_template("data.html", _id = user["_id"], username = user["user"], status = 0);
               else:
                       return redirect(url_for("login"))
    else:
           return redirect(url_for("login"))

#################################### ERROR ####################################
@app.errorhandler(404)
def page_not_found(error):
    return "404 :: Page not found"

