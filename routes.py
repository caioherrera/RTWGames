from flask import Flask, request, render_template, url_for
from app import app

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", nome=nome)