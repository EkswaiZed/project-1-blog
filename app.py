from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
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

@app.route('/')
def home():
    posts = db.session.execute(
        db.select(Post).order_by(Post.date_created.desc())
    ).scalars().all()
    return render_template("index.html", posts=posts)

if __name__ == '__main__':
    app.run(debug=True)