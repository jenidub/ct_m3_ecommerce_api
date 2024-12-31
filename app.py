# PROJECT LIBRARY IMPORT STATEMENTS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields

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
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id"))
    
    # Many to One Relationship: List of Orders => 1 User
    user: Mapped["User"] = relationship(back_populates="orders")
    
    # One to Many: 1 Order => List of Products
    order_products: Mapped[List["Product"]] = relationship(secondary=order_product, back_populates="product_orders")
    
# => PRODUCT TABLE
# id:Integer, primary key, auto-increment
# ● product_name: String
# ● price: Float

class Product(Base):
    __tablename__ = "app_products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # One to Many: 1 Product => List of Orders
    product_orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="order_products")

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
    id = ma.auto_field(dump_only=True)
    user_id = fields.Integer()

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
# [1] CREATE NEW USER
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
# ● GET /users: Retrieve all users
@app.route("/users", methods=["GET"])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    return users_schema.jsonify(users), 200

# ● GET /users/<id>: Retrieve a user by ID
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

## PRODUCT ENDPOINTS ##
# [1] CREATE NEW PRODUCT
# ● POST /products: Create a new product
@app.route("/products", methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(product_name=product_data["product_name"], price=product_data["price"])
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 200

# [2] PRODUCT GET INFO
# ● GET /products: Retrieve all products
@app.route("/products", methods=["GET"])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    return products_schema.jsonify(products), 200

# ● GET /products/<id>: Retrieve a product by ID
@app.route("/products/<id>", methods=["GET"])
def get_product(id):
    product = db.session.get(Product, id)
    return product_schema.jsonify(product), 200

# [3] UPDATE PRODUCT INFO
# ● PUT /products/<id>: Update a product by ID
@app.route("/products/<id>", methods=["PUT"])
def update_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "Invalid product ID"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data["product_name"]
    product.price = product_data["price"]
    
    db.session.commit()
    return product_schema.jsonify(product), 200

# [4] DELETE PRODUCT INFO
# ● DELETE /products/<id>: Delete a product by ID
@app.route("/products/<id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "ID not found"}), 400
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted product ID {id}"}), 200

## ORDER ENDPOINTS ##
# [1] CREATE NEW ORDER
# ● POST /orders: Create a new order (requires user ID and order date)
@app.route("/orders", methods=["POST"])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(user_id=order_data["user_id"])
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 200

# [2] GET ORDER INFO
# ● GET /orders/<order_id>/add_product/<product_id>: Add a product to an order
# === TO DO: (prevent duplicates) === #
@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["GET"])
def add_product(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": f"Order ID {order_id} not found"}), 400
    
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": f"Product ID {product_id} not found"}), 400   

    if product not in order.order_products:
        order.order_products.append(product)
        db.session.commit()
        return jsonify({"message": f"{product.product_name} was added to order #{order_id} for user #{order.user_id}"}), 200
    else:
        return jsonify({"message": f"{product.product_name} is already in order #{order_id}"}), 400

# ● GET /orders/user/<user_id>: Get all orders for a user
@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    query = db.session.query(Order).filter_by(user_id=user_id)
    orders = query.all()
    if not orders:
        return jsonify({"message": f"User ID {user_id} not found"}), 400
    return orders_schema.jsonify(orders), 200

# ● GET /orders/<order_id>/products: Get all products for an order
@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)
    products = order.order_products
    if not products:
        return jsonify({"message": f"Order ID {order_id} not found"}), 400
    return products_schema.jsonify(products), 200

# [3] DELETE a PRODUCT from an ORDER
# ● DELETE /orders/<id:order_id>/remove_product/<id:<product_id> Remove a product from an order
@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def delete_order_product(order_id, product_id):
    order = db.session.query(Order).get(order_id)
    product = db.session.query(Product).get(product_id)

    if product in order.order_products:
        order.order_products.remove(product)
        db.session.commit()
        return jsonify({"message": f"Association between {order_id} and {product_id} successfully removed"}), 200
    else:
        return jsonify({"message": f"Association not found"}), 400

# SESSION FIX for BAD RELATIONSHIP
# with app.app_context():
#     # db.drop_all() # Delete all tables
#     db.create_all() # Create all of the tables

# === LAUNCH API === #
# Only run if this is the current file
if __name__ == "__main__":
    with app.app_context():
    #     #db.drop_all() # Delete all tables
        db.create_all() # Create all of the tables
    app.run(debug=True)
