# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)
app.config.from_object("app.settings")  # need for secret key
from app import views
