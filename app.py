from flask import Flask, make_response, request
from flask_migrate import Migrate

from models import db, User, Flight, Hotel, UserHotel, Booking

# Initialize the flask application
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
