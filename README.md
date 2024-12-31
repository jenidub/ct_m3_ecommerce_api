# eCommerce API
The following eCommerce API was built using Flask and Flask-Marshmallow, connected to a MySQL database. It provides functionality to manage users, products, and orders, including CRUD operations and associations between these entities.

## Features

- User management (Create, Read, Update, Delete)
- Product management (Create, Read, Update, Delete)
- Order management, including:
  - Creating orders
  - Adding products to orders
  - Viewing products in orders
  - Removing products from orders
- Relationships between users, products, and orders managed via SQLAlchemy
- Input validation with Marshmallow schemas

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database:**
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.py` to match your MySQL credentials and database name:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<username>:<password>@<host>/<database>'
     ```

5. **Initialize the database:**
   ```bash
   python app.py
   ```
   The `db.create_all()` call in the script will create the necessary tables.

## Requirements

Dependencies are listed in `requirements.txt`:

- Flask==3.1.0
- flask-marshmallow==1.2.1
- Flask-SQLAlchemy==3.1.1
- mysql-connector-python==9.1.0
- marshmallow==3.23.2
- marshmallow-sqlalchemy==1.1.0
- SQLAlchemy==2.0.36

Refer to `requirements.txt` for the full list and versions.

## Usage

1. **Run the application:**
   ```bash
   python app.py
   ```

2. **Access the API:**
   - Base URL: `http://localhost:5000`

### API Endpoints

#### User Endpoints
- `POST /users`: Create a new user
- `GET /users`: Retrieve all users
- `GET /users/<id>`: Retrieve a user by ID
- `PUT /users/<id>`: Update a user by ID
- `DELETE /users/<id>`: Delete a user by ID

#### Product Endpoints
- `POST /products`: Create a new product
- `GET /products`: Retrieve all products
- `GET /products/<id>`: Retrieve a product by ID
- `PUT /products/<id>`: Update a product by ID
- `DELETE /products/<id>`: Delete a product by ID

#### Order Endpoints
- `POST /orders`: Create a new order
- `GET /orders/<order_id>/add_product/<product_id>`: Add a product to an order
- `GET /orders/user/<user_id>`: Get all orders for a user
- `GET /orders/<order_id>/products`: Get all products in an order
- `DELETE /orders/<order_id>/remove_product/<product_id>`: Remove a product from an order

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- Flask framework documentation: [Flask Docs](https://flask.palletsprojects.com/)
- SQLAlchemy ORM: [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- Marshmallow for serialization: [Marshmallow Docs](https://marshmallow.readthedocs.io/)
- ChatGPT for the creation of the README file

## Contributions

Contributions are welcome! Feel free to fork this repository and submit a pull request with your improvements.

