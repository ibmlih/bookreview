import os, requests, ast

from password import isStrongPassword
from flask import Flask, session, request, render_template, g, redirect, url_for, jsonify
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
    # Trying to login
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Checking if username and password exist
        if db.execute('SELECT "username", "password" FROM "user" WHERE "username" = :username\
            and "password" = :password', {"username": username, "password":password}).rowcount == 1:

            # Logging in
            session["user"] = username
            return redirect(url_for('search'))

        # Error
        else:
            return render_template("error.html", msg="Username or password invalid.", url="index")

    # Already logged in
    elif 'user' in session:
        return redirect(url_for('search'))

    else:
        return render_template("index.html")


@app.route("/search", methods=['GET', 'POST'])
def search():
    # Display Search Bar
    if g.user and request.method == 'GET':
        return render_template("search.html")

    # Searching
    elif g.user and request.method == 'POST':
        search = request.form.get("search")
        return redirect(url_for('display', search=search))

    # Not logged in
    else:
        return render_template("error.html", msg="Please login first.", url="index")


@app.route("/search/<string:search>")
def display(search):
    if g.user:
        result = db.execute('SELECT "title", "author", "year", "isbn" FROM "book" WHERE UPPER("title") LIKE UPPER(:search)\
            OR UPPER("author") LIKE UPPER(:search) OR UPPER("isbn") LIKE UPPER(:search)', {"search":'%'+search+'%'}).fetchall()

        return render_template("display.html", result=result)

    else:
        return render_template("error.html", msg="Please login first.", url="index")


@app.route("/bookinfo", methods=['GET', 'POST'])
def bookinfo():
    if g.user and (request.method == "GET" or request.method == "POST"):
        title = request.args.get("title")
        author = request.args.get("author")
        year = request.args.get("year")
        isbn = request.args.get("isbn")

        if request.method == "POST":
            rating = request.form.get("rating")
            review = request.form.get("review")
            username = str(g.user)

            # No ratings selected
            if rating == "Ratings":
                return render_template("error.html", msg="Please rate the book.", url="search")

            # Already submitted a review
            if isBookInBookreview(isbn):
                usernameList = str(db.execute('SELECT "usernames" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())
                usernameList = usernameList[2:len(usernameList) - 3]
                usernameList = ast.literal_eval(usernameList)

                if username in usernameList:
                    return render_template("error.html", msg="You already reviewed this book.", url="search")

            # No optional review
            if not review:

                # If the book exists in the table
                if isBookInBookreview(isbn):
                    usernames = str(db.execute('SELECT "usernames" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())
                    usernames = usernames[2:len(usernames) - 3]
                    usernames = ast.literal_eval(usernames)
                    usernames.append(username)
                    usernames = str(usernames)

                    db.execute('UPDATE "bookreview" SET "ratings" = "ratings" + :ratings, "ratingsNum" = "ratingsNum" + 1, "usernames" = :usernames WHERE \
                    "isbn"=:isbn', {"ratings":rating, "usernames":usernames, "isbn":isbn})
                    db.commit()

                # Book does not exist
                else:
                    usernameList = [username]
                    usernameString = str(usernameList)
                    # Insert into database
                    db.execute('INSERT INTO "bookreview" ("isbn", "ratings", "ratingsNum", "usernames") VALUES (:isbn, :ratings, :ratingsNum, :username)',
                        {"isbn":isbn, "ratings":rating, "ratingsNum": 1, "username":usernameString})
                    db.commit()

            # Optional review
            else:
                # If the book exists in the table
                if isBookInBookreview(isbn):
                    usernames = str(db.execute('SELECT "usernames" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())
                    usernames = usernames[2:len(usernames) - 3]
                    usernames = ast.literal_eval(usernames)
                    usernames.append(username)
                    usernames = str(usernames)

                    reviews = str(db.execute('SELECT "reviews" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())
                    temp = reviews[1:len(reviews) - 2]

                    # The book exists but no reviews yet
                    if temp == "None":
                        reviews = str({username:review})

                    # The book has a review already
                    else:
                        reviews = reviews[2:len(reviews) - 3]
                        reviews = ast.literal_eval(reviews)
                        reviews[username] = review
                        reviews = str(reviews)

                    db.execute('UPDATE "bookreview" SET "ratings" = "ratings" + :ratings, "ratingsNum" = "ratingsNum" + 1, "usernames" = :usernames, "reviews" = :reviews WHERE \
                    "isbn" = :isbn', {"ratings":rating, "usernames":usernames, "reviews":reviews, "isbn":isbn})
                    db.commit()

                # Book does not exist
                else:
                    usernameList = [username]
                    usernameString = str(usernameList)
                    reviews = str({username:review})

                    # Insert into database
                    db.execute('INSERT INTO "bookreview" ("isbn", "ratings", "ratingsNum", "usernames", "reviews") VALUES (:isbn, :ratings, :ratingsNum, :username, :reviews)',
                        {"isbn":isbn, "ratings":rating, "ratingsNum": 1, "username":usernameString, "reviews":reviews})
                    db.commit()



        ######

        rating, ratingNum, avgRating = 0, 0, 0.0
        reviews2 = {}

        # Check if the book exists in the table
        # Then gets the ratings from the database
        if isBookInBookreview(isbn):
            rating = list(db.execute('SELECT "ratings" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())[0]
            ratingNum = list(db.execute('SELECT "ratingsNum" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())[0]
            avgRating = round( int(rating) / int(ratingNum), 2)

            reviews2 = str(db.execute('SELECT "reviews" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).fetchone())
            temp = reviews2[1:len(reviews2) - 2]

            if temp != "None":
                reviews2 = reviews2[2:len(reviews2) - 3]
                reviews2 = ast.literal_eval(reviews2)

        # Goodreads API
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
        average_rating = res.json()['books'][0]['average_rating']
        number_rating = res.json()['books'][0]['work_ratings_count']

        return render_template("bookinfo.html", title=title, author=author, year=year, isbn=isbn,
            average_rating=average_rating, number_rating=number_rating, avgRating=avgRating, ratingNum=ratingNum, reviews=reviews2)


    else:
        return render_template("error.html", msg="Please login first.", url="index")


def isBookInBookreview(isbn):
    return db.execute('SELECT "isbn" FROM "bookreview" WHERE "isbn" = :isbn', {"isbn": isbn}).rowcount > 0


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

        # Username cannot contain special characters
        if not username.isalnum():
            return render_template("error.html", msg="Username cannot contain special characters.", url="signup")

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


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
