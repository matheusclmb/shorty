from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()


class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(6))

    def __init__(self, long, short):
        self.long = long
        self.short = short


@app.before_first_request
def create_tables():
    db.create_all()


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    numbers = string.digits
    while True:
        randomizer = "".join(random.choices(letters + numbers, k=6))
        short_url = Urls.query.filter_by(short=randomizer).first()
        if not short_url:
            return randomizer


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        url_received = request.form["name"]
        # CHECK IF URL ALREADY EXIST IN DB
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            return render_template("index.html", short_url_display=found_url.short)
        else:
            # CREATE SHORT URL IF NOT FOUND
            short_url = shorten_url()
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return render_template("index.html", short_url_display=short_url)

    else:
        return render_template("index.html")


@app.route("/display/<url>")
def display_short_url(url):
    return render_template("shorturl.html", short_url_display=url)


@app.route("/<short_url>")
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return render_template("notfound.html")


if __name__ == "__main__":
    app.run(debug=True)
