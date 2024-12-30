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
    __tablename__ = "app_users"
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
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id"))
    
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

# === API ENDPOINTS === #
## USER ENDPOINTS ##
# [1] CREATE NEW USER ENDPOINT
# ● POST /users: Create a new user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_user = User(name=user_data["name"], address=user_data["address"], email=user_data["email"])
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user), 200

# [2] GET USER INFO ENDPOINTS
# => GET /users: Retrieve all users
@app.route("/users", methods=["GET"])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    return users_schema.jsonify(users), 200

# => GET /users/<id>: Retrieve a user by ID
@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

# [3] UPDATE USER INFO by ID
# ● PUT /users/<id>: Update a user by ID
@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "Invalid user ID"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data["name"]
    user.address = user_data["address"]
    user.email = user_data["email"]
    
    db.session.commit()
    return user_schema.jsonify(user), 200

# [4] DELETE USER ACCOUNT
# ● DELETE /users/<id>: Delete a user by ID
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted User ID {id}"}), 200

# LAUNCH API - Only run if this is the current file
if __name__ == "__main__":
    with app.app_context():
        #db.drop_all() # Delete all tables
        db.create_all() # Create all of the tables
    
    app.run(debug=True)