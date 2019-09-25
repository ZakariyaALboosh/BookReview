import os
import requests
from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
app = Flask(__name__)




os.environ["DATABASE_URL"] ="postgres://hcltwivjzhqgxy:458fc2856e29de6a0e1690166b7014ab620cd1291c8d6de457c6412569106977@ec2-46-137-113-157.eu-west-1.compute.amazonaws.com:5432/d66c21bt7mpp2r"
DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
#Set API key for goodreads
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5VS6LlAyvuYBQLUUzT4RFA", "isbns": "9781632168146"})
print(res.json())
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return "Project 1: TODO"



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
#self explanatory
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return 403

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                         {"username": request.form.get("username")} ).fetchone()
        
        
        # Ensure username exists and password is correct
        if  not rows or not check_password_hash(rows[2], request.form.get("password")):
            return apology("wrong user or pass ", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]
        session["username"] = rows[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
       
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not username or not password or not confirm:
            return apology("All fields required")
        if password != confirm:
            return apology("password doesn't match")
        passhash = generate_password_hash(password)
        query =  db.execute("SELECT username from users WHERE username = :userin", {"userin" : username}).fetchall()
        

        if not query:
            result = db.execute("INSERT INTO users(username,hash) VALUES(:username, :phash)", {"username" : username , "phash" :passhash})
            if not result:
                return apology("database error")
            new = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchone()
            print(new)
            session["user_id"] = new[0]
            session["username"] = new[1]
            db.commit()
            return redirect("/")
           
        else:
            return apology("username taken", 400)
            db.commit()
    return render_template("register.html")


