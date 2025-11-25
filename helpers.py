import requests

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session

def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code