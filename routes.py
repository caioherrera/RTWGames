from __future__ import print_function
from flask import Flask, request, render_template, url_for, redirect, session
from app import app, mongo
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
    return


#################################### PEOPLE ####################################
@app.route("/people")
def people():
    return


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
					return render_template("firstGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
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
				print("a", file = sys.stderr)
				return render_template("secondGame.html", username = user["user"], code = 2, theme = theme, game = str(game), _id = str(user["_id"]), data = data2)
			else:
				idGame = -1
				theme = ""
				status = 4
				if len(game) != 24:
					print("b", file = sys.stderr)
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
						print("c", file = sys.stderr)
						return render_template("secondGame.html", username = user["user"], code = 10, theme = theme, game = idGame, _id = str(user["_id"]), score = int(game["score1"]))
					else:
						print("d", file = sys.stderr)
						return render_template("secondGame.html", username = user["user"], code = 1, theme = theme, game = idGame, _id = str(user["_id"]))
				else:
					print("e", file = sys.stderr)
					return render_template("secondGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]))
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
		print("ok", file = sys.stderr)
	else:
		#change it later
		updates["data1"] = str(request.form["data1"]).encode("UTF-8")		
	print("identification: " + str(identifications), file = sys.stderr)
	print("updates: " + str(updates), file = sys.stderr)
	updateGame(identifications, updates)
	finishGame(identifications)
	if number == 1:
		return redirect(url_for("firstGame", game = str(identifications["_id"])))
	elif number == 2:
		return redirect(url_for("secondGame", game = str(identifications["_id"])))
	#change it later
	return "Hello"


#################################### UPDATE ####################################
@app.route("/update")
def update():

	'''mongo.db.feedbacks.remove({})
	mongo.db.games.remove({})
	mongo.db.subcategories.remove({})
	mongo.db.categories.remove({})

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

	#mongo.db.games.remove({"gameType": 2})
	#mongo.db.feedbacks.remove({"category": "movie"})

	cursor = mongo.db.categories.find({})
	string = str()
	for category in cursor:
		string += category["name"] + ": "
		cursor2 = mongo.db.subcategories.find({"category": category["_id"]})
		for subcategory in cursor2:
			string += "<li>" + subcategory["name"] + "</li>"
		string += "<br>"
	string += "<hr>"
	
	cursor = mongo.db.feedbacks.find({})
	for fb in cursor:
		string += str(fb) + "<br><br>"

	cursor = mongo.db.games.find({"gameType": 2})
	for c in cursor:
		string += str(c)
	
	return string


#################################### ERROR ####################################
@app.errorhandler(404)
def page_not_found(error):
    return "404 :: Page not found"
