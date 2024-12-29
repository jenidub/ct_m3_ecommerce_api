from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

import os

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, String, Column, select, DateTime
from typing import List

# INIT FLASK APP
app = Flask(__name__)

# APP CONFIG via SQL ALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:JWhod94612!@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === CREATE DATA BASE MODEL ===
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

