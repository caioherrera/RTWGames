from flask import Flask
from flask.ext.pymongo import MongoClient

app = Flask("RTWGames")

app.secret_key = "APIBG-Ge0-dha-1\h09-wqx[sj'n1"

mongo = ""#PyMongo(app)
client = MongoClient('mongodb://admin:herrera!@ds017553.mlab.com:17553/rtwgames', connect=False)
db = client.rtwgames

wsgi_app = app.wsgi_app

from routes import *

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True, threaded=True)


