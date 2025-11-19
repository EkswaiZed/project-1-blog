from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "My Blog - Coming Soon"

if __name__ == '__main__':
    app.run(debug=True)