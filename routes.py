#!/usr/bin/env python3
from __future__ import print_function
import json
from flask import request, render_template, url_for, redirect, session, jsonify
from app import app, db
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
            return render_template("index.html", code = 1, username = session["user"], admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("index.html", code = 0, admin = False)

#################################### ADMIN ####################################
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        if isUserOnline(identifications):
            if isUserAdmin(identifications):

                if request.method == "POST":
                    form = int(request.form["form"])
                    if form == 0:
                        createSeed(request.form["entity"], request.form["category"])
                        return render_template("admin.html", username = session["user"], form1 = 1, form2 = 0)
                    else:
                        #new admin
                        identifications = dict()
                        identifications["user"] = request.form["user"]
                        identifications["email"] = request.form["email"]
                        newAdm = getUser(identifications)

                        if newAdm == None:
                            return render_template("admin.html", username = session["user"], form1 = 0, form2 = 1)
                        elif newAdm["permission"] == 1:
                            return render_template("admin.html", username = session["user"], form1 = 0, form2 = 2)
                        else:
                            updates = dict()
                            updates["permission"] = 1
                            updateUser(identifications, updates)
                            return render_template("admin.html", username = session["user"], form1 = 0, form2 = 3)
                else:
                    return render_template("admin.html", username = session["user"], form1 = 0, form2 = 0)
            else:
                return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#################################### PROFILE ####################################
@app.route("/profile")
def profile():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        if isUserOnline(identifications):
            user = getUser(identifications)
            return render_template("profile.html", _id = user["_id"], username = user["user"], email = user["email"], score = user["score"], regDate = user["regDate"], admin = isUserAdmin({"user": session["user"]}))
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
        identifications["email"] = request.form["user"]
        identifications["password"] = toHash(request.form["password"])
        user = getUser(identifications)
        if user != None:
            changeUserStatus(identifications, True)
            session["user"] = user["user"]
            return render_template("login.html", code = 1, username = user["user"], admin = isUserAdmin({"user": session["user"]}))
        else:
            identifications = dict()
            identifications["user"] = request.form["user"]
            identifications["password"] = toHash(request.form["password"])
            user = getUser(identifications)
            if user != None:
                changeUserStatus(identifications, True)
                session["user"] = user["user"]
                return render_template("login.html", code = 1, username = user["user"], admin = isUserAdmin({"user": session["user"]}))
            else:
                return render_template("login.html", code = 2)

#################################### REGISTER ####################################
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", code = 0)
    elif request.method == "POST":

        email = request.form["email"]
        user = request.form["user"]
        password = request.form["password"]
        permission = 0
        confPassword = request.form["confPassword"]
        if not password == confPassword:
            return render_template("register.html", code = 2)
        elif getUser({"user": request.form["user"]}) != None:
            return render_template("register.html", code = 3)
        elif getUser({"email": request.form["email"]}) != None:
            return render_template("register.html", code = 4)
        else:
            if createUser(email, user, toHash(password), permission) != None:
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
            return render_template("overview.html", code = 1, username = session["user"], admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("overview.html", code = 0)

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
            return render_template("games.html", username = session["user"], admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#################################### FIRST GAME ####################################
@app.route("/firstGame")
def firstGame():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        user = getUser(identifications)
        if user != None:
            identifications = dict()
            identifications["gameType"] = 1
            game = findWaitingGame(identifications, user["_id"])
            if game == None:
                category = pickRandomCategory()
                theme = category["name"][0]
                identifications = dict()
                identifications["gameType"] = 1
                identifications["theme"] = theme
                game = createGame(identifications)
                identifications["_id"] = game
                joinGame(identifications, user["_id"])
                return render_template("firstGame.html", theme = theme, game = str(game), _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}))
            else:
                identifications = dict()
                identifications["_id"] = game["_id"]
                joinGame(identifications, user["_id"])
                theme = game["theme"]
                if isGameReady(identifications):
                    startGame(identifications)
                return render_template("firstGame.html", theme = theme, game = str(game["_id"]), _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#################################### SECOND GAME ####################################
@app.route("/secondGame")
def secondGame():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        user = getUser(identifications)
        if user != None:
            identifications = dict()
            category = pickRandomCategory()
            themes = category["name"]
            theme = themes[0]

            strThemes = "||".join(themes) + "||"
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
            for i in getData(dataId, sortCriteria, maxValues):
                if not first:
                    data2 += "||"
                first = False
                data2 += str(i)

            startGame(identifications)
            return render_template("secondGame.html", themes = strThemes, game = str(game), _id = str(user["_id"]), data = data2, admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#################################### THIRD GAME A ####################################
@app.route("/thirdGameA")
def thirdGameA():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        user = getUser(identifications)
        if user != None:
            identifications = dict()
            identifications["gameType"] = 3
            game = findWaitingGame(identifications, user["_id"])
            if game == None:

                category = pickRandomCategory()
                dataId = dict()
                dataId["category"] = category["name"][0]
                sortCriteria = [("score", 1)]
                maxValues = 10
                theme1 = pickRandomFeedback(dataId, sortCriteria, maxValues)
                theme2 = theme1
                while theme2 == theme1:
                    theme2 = pickRandomFeedback(dataId, sortCriteria, maxValues)

                identifications = dict()
                themes = (theme1, theme2)
                identifications["theme"] = themes
                identifications["gameType"] = 3
                game = createGame(identifications)
                identifications["_id"] = game
                joinGame(identifications, user["_id"])
                return render_template("thirdGameA.html", theme = themes, game = str(game), _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}), user = 1)

            else:
                identifications = dict()
                identifications["_id"] = game["_id"]
                joinGame(identifications, user["_id"])
                if isGameReady(identifications):
                    startGame(identifications)
                return render_template("thirdGameA.html", theme = game["theme"], game = str(game["_id"]), _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}), user = 2)

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
                    return render_template("secondGame.html", username = user["user"], code = status, theme = theme, game = idGame, _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}))
                identifications = dict()
                identifications["_id"] = ObjectId(game)
                identifications["gameType"] = 3
                game = getGame(identifications)
                if game != None:
                    if user["_id"] == userFromGame(identifications, 1)["_id"]:
                        data = game["data2"]
                        theme = game["theme"].split("||")[1]
                    elif user["_id"] == userFromGame(identifications, 2)["_id"]:
                        data = game["data1"]
                        theme = game["theme"].split("||")[0]
                    else:
                        return render_template("thirdGameB.html", username = user["user"], code = 7, theme = theme, game = idGame, _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}))
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
                    return render_template("thirdGameB.html", username = user["user"], code = 2, theme = theme, game = idGame, _id = str(user["_id"]), data = data, admin = isUserAdmin({"user": session["user"]}))
                else:
                    return render_template("thirdGameB.html", username = user["user"], code = 4, theme = theme, game = idGame, _id = str(user["_id"]), admin = isUserAdmin({"user": session["user"]}))
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
        if userFromGame(identifications, 1)["_id"] == user:
            updates["data1"] = str(request.form["data"]).encode("UTF-8")
        else:
            updates["data2"] = str(request.form["data"]).encode("UTF-8")
    elif number == 2:
        updates["data1"] = str(request.form["data1"]).encode("UTF-8")
        updates["data2"] = str(request.form["data2"]).encode("UTF-8")
        updates["score1"] = int(request.form["score"])
        updates["score2"] = int(request.form["count"])
    elif number == 3:
        if userFromGame(identifications, 1)["_id"] == user:
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
        #print("retornando pro jogo 2", file=sys.stderr);
        return redirect(url_for("secondGame", game = str(identifications["_id"])))
    elif number == 3:
        return redirect(url_for("thirdGameA", game = str(identifications["_id"])))
    else:
        #return redirect(url_for("thirdGameB", game = str(identifications["_id"]))
        identifications = dict()
        identifications["_id"] = user
        user = getUser(identifications)
        return render_template("thirdGameB.html", username = user["user"], code = 1, score = updates["score1"], game = str(identifications["_id"]), _id = user["_id"], admin = isUserAdmin({"user": session["user"]}))

'''#################################### UPDATE ####################################
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


    mongo.db.feedbacks.remove({})
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
    mongo.db.subcategories.insert_one({"name": "Rock musics", "category": cursor[0]["_id"]})

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

    return string'''

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
            score = 0.0
        updates["isInNell"] = exists
        updates["score"] = score
        #mongo.db.feedbacks.update_one(identifications, {"$set": updates})
        db.feedbacks.update_one(identifications, {"$set": updates})

    return str(i) + " registers updated."

#################################### DATA ####################################
@app.route("/data", methods=["GET", "POST"])
def data():
    if session.get("user"):
        identifications = dict()
        identifications["user"] = session["user"]
        if isUserOnline(identifications):
            return render_template("data.html", username = session["user"], admin = isUserAdmin({"user": session["user"]}))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#################################### GENERATE DATA ####################################
@app.route("/generateData", methods=["GET"])
def generateData():
    search = request.args["search"]
    gameType = int(request.args["gameType"])
    position = int(request.args["position"])
    count = int(request.args["count"])
    score = float(request.args["score"])

    queryReturn = list()
    identifications = dict()
    if gameType != 4:
        identifications["gameType"] = gameType
    if position in [0, 1]:
        if len(search) > 0:
            identifications["entity"] = search
        identifications["count"] = { "$gte": count }
        identifications["score"] = { "$gte": score }
        cursor = db.feedbacks.find(identifications)
        for item in cursor:
            jsonItem = dict()
            jsonItem["category"] = item["category"]
            jsonItem["entity"] = item["entity"]
            jsonItem["count"] = item["count"]
            jsonItem["gameType"] = item["gameType"]
            jsonItem["isInNell"] = item["isInNell"]
            jsonItem["score"] = item["score"]
            jsonItem["lazy"] = item["lazy"]
            queryReturn.append(jsonItem)

    identifications = dict()
    if gameType != 4:
        identifications["gameType"] = gameType
    if position in [0, 2]:
        if len(search) > 0:
            identifications["category"] = search
        identifications["count"] = { "$gte": count }
        identifications["score"] = { "$gte": score }
        cursor = db.feedbacks.find(identifications)
        for item in cursor:
            jsonItem = dict()
            jsonItem["category"] = item["category"]
            jsonItem["entity"] = item["entity"]
            jsonItem["count"] = item["count"]
            jsonItem["gameType"] = item["gameType"]
            jsonItem["isInNell"] = item["isInNell"]
            jsonItem["score"] = item["score"]
            jsonItem["lazy"] = item["lazy"]
            queryReturn.append(jsonItem)

    return "<pre>" + str(json.dumps(queryReturn, ensure_ascii=False, indent=1)) + "</pre>"

#################################### ERROR ####################################
@app.errorhandler(404)
def page_not_found(error):
    return "404 :: Page not found"








@app.route("/ajax_isGameReady", methods=["POST"])
def ajax_isGameReady():
    data = request.get_json()
    gameID = ObjectId(data["gameID"])

    identifications = dict()
    identifications["_id"] = gameID

    return jsonify(result=isGameReady(identifications))


@app.route("/ajax_isGameOver", methods=["POST"])
def ajax_isGameOver():
    data = request.get_json()
    gameID = ObjectId(data["gameID"])
    userID = ObjectId(data["userID"])

    identifications = dict()
    identifications["_id"] = gameID

    score = -1
    enemyScore = -1
    if checkGameStatus(identifications) == 1:
        game = getGame(identifications)

        if game["winner"] == None:
            enemyScore = 0
            score = game["score1"]

        else:
            if game["user1"]["_id"] == userID:
                score = game["score1"]
                enemyScore = game["score2"]
            else:
                score = game["score2"]
                enemyScore = game["score1"]

    return jsonify(myScore=score, opponentScore=enemyScore)


@app.route("/ajax_saveData", methods=["POST"])
def ajax_saveData():
    data = request.get_json()
    gameID = ObjectId(data["gameID"])
    userID = ObjectId(data["userID"])
    gameType = int(data["gameType"])

    identifications = dict()
    identifications["_id"] = gameID

    updates = dict()

    if gameType == 1:
        if userFromGame(identifications, 1)["_id"] == userID:
            updates["data1"] = data["data"]
        else:
            updates["data2"] = data["data"]
    elif gameType == 2:
        updates["data1"] = data["data"]
        updates["score1"] = int(data["score"])
    elif gameType == 3:
        if userFromGame(identifications, 1)["_id"] == userID:
            updates["data1"] = data["data"]
            updates["score1"] = int(data["score"])
        else:
            updates["data2"] = data["data"]
            updates["score2"] = int(data["score"])

    r = (updateGame(identifications, updates) and finishGame(identifications))

    return jsonify(result=r)

@app.route("/ajax_getData", methods=["POST"])
def ajax_getData():
	data = request.json()
	user = int(data["user"])
	gameID = ObjectId(data["gameID"])
		
	identifications = dict()
	identifications["_id"] = gameID

	game = getGame(identifications)
	if user == 1:
		return jsonify(data = game["data1"])
	else:
		return jsonify(data = game["data2"])
