import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from helpers import apology, login_required

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
# initialize the app with the extension
db.init_app(app)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(65536))
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="posts")

with app.app_context():
    db.create_all()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    
    username = db.session.execute(
        db.select(User.username).where(User.id == user_id)
    ).scalar_one_or_none()
    
    posts = db.session.execute(
        db.select(Post).order_by(Post.date_created.desc())
    ).scalars().all()
    return render_template("index.html", posts=posts, username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not request.form.get("username"):
            return apology("must provide username", 400)
        
        if not request.form.get("email"):
            return apology("must provide email", 400)
        
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("must confirm password")

        if password != confirmation:
            return apology("passwords must match") 
        
        user = User(
            username = username,
            email = email,
            password = generate_password_hash(password),
        )    
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return apology("username or email are already taken", 400)

        return redirect("/")

    else:
        return render_template("register.html")   

@app.route("/login", methods=["GET", "POST"])
def login():
    
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        if not request.form.get("password"):
            return apology("must provide password", 403)

        user = db.session.execute(
            db.select(User).filter_by(username=request.form.get("username"))
                ).scalar_one_or_none()
        
        if user is None or not check_password_hash(
            user.password, request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Login successful!')

        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash('Logged out successfully!')
    # Redirect user to login form
    return redirect("/login")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    if 'user_id' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        new_post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        
        flash('Post created successfully!')
        return redirect(url_for('index'))
    
    return render_template('create_post.html')

if __name__ == '__main__':
    app.run(debug=True)