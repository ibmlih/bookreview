import os

from password import isStrongPassword
from flask import Flask, session, request, render_template, g, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Goodreads Key
KEY = '11lde3d29lqXUBzAdHwQ'

# Home
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Checking if username and password exist
        if db.execute('SELECT "username", "password" FROM "user" WHERE "username" = :username\
            and "password" = :password', {"username": username, "password":password}).rowcount == 1:
            session["user"] = username
            return redirect(url_for('search'))
        else:
            return render_template("error.html", msg="Username or password invalid.", url="index")

    elif 'user' not in session:
        return render_template("index.html")

    else:
        return redirect(url_for('search'))


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route("/search")
def search():
    # If logged in
    if g.user:
        return render_template("search.html")
        
    else:
        return render_template("error.html", msg="Please login first.", url="index")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")

        # One of the fields empty.
        if (username is "") or (password is "") or (confirmpassword is ""):
            return render_template("error.html", msg="One of the fields is empty.", url="signup")

        # Username must be at least 4 characters long.
        if len(username) < 4:
            return render_template("error.html", msg="Username must be at least 4 characters long.", url="signup")

        # Checking if username already exists
        if db.execute('SELECT "username" FROM "user" WHERE "username" = :username',
            {"username": username}).rowcount > 0:
            return render_template("error.html", msg="The username already exists.", url="signup")

        # Check if it is a strong password
        if not isStrongPassword(password):
            return render_template("error.html", msg="Your password must be at least 6 characters and at most 20 characters, and contain\
             at least one lowercase letter, at least one uppercase letter, and at least one digit.", url="signup")

        # Check if the password match
        if not password == confirmpassword:
            return render_template("error.html", msg="Your password does not match.", url="signup")

        # Insert into database
        db.execute('INSERT INTO "user" ("username", "password") VALUES (:username, :password)',
            {"username":username, "password":password})
        db.commit()

        session["user"] = username

        return redirect(url_for('search'))

    else:
        return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))
