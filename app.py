# PROJECT LIBRARY IMPORT STATEMENTS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

import os

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, String, Column, select, DateTime, Float
from typing import List
from datetime import datetime

# ===  API CONFIGURATION === #
# INIT FLASK APP
app = Flask(__name__)

# APP CONFIG via SQL ALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:JWhod94612!@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === CREATE DATA BASE MODEL === #
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

## TABLE DEFINITIONS ##
# => ORDER PRODUCT ASSOCIATION TABLE
# ● order_id:Integer,foreign key referencing Order
# ● product_id:Integer,foreign key referencing Product

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("app_orders.id")),
    Column("product_id", ForeignKey("app_products.id"))
)

# => USER TABLE
# id:Integer, primary key, auto-increment
# name: String
# address: String
# email: String (must be unique)

class User(Base):
    __tablename__ = "user_accounts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    
    #One to Many Relationship: 1 User => List of Orders
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

# => ORDER TABLE
# ● id: Integer, primary key, auto-increment
# ● order_date: DateTime (learn to use DateTime in SQLAlchemy)
# ● user_id: Integer, foreign key referencing User

class Order(Base):
    __tablename__ = "app_orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"))
    
    # Many to One Relationship: List of Orders => 1 User
    user: Mapped["User"] = relationship(back_populates="orders")

# => PRODUCT TABLE
# id:Integer, primary key, auto-increment
# ● product_name: String
# ● price: Float

class Product(Base):
    __tablename__ = "app_products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

# === MARSHMALLOW SCHEMA DEFINITIONS === #
## SCHEMA DEFINITIONS ##
# ● UserSchema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

# ● OrderSchema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        
# ● ProductSchema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

## INIT SCHEMAS ##
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

