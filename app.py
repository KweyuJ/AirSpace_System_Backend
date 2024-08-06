from datetime import datetime
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Flight, Hotel, UserFlight, UserHotel, Booking
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airescape.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

api = Api(app)

# Decorator for Admin Access
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        if user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

class Index(Resource):
    def get(self):
        response_dict = {"message": "Welcome to the AirEscape RESTful API"}
        return make_response(jsonify(response_dict), 200)

api.add_resource(Index, '/')

class Users(Resource):
    def get(self):
        # Admins should be able to list all users
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        if user.role != 'admin':
            return make_response(jsonify({"error": "Admin access required"}), 403)
        users = User.query.all()
        response = [user.to_dict() for user in users]
        return make_response(jsonify(response), 200)

    def post(self):
        data = request.get_json()
        email = data['email']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return make_response(jsonify({"error": "Email already exists"}), 422)

        new_user = User(
            title=data.get('title'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=email,
            password=bcrypt.generate_password_hash(data.get("password")).decode('utf-8'),
            role=data.get('role', 'traveler'),
            phone_number=data['phone_number']
        )
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.user_id)  

        response = {
            "user": new_user.to_dict(),
            "access_token": access_token
        }

        return make_response(jsonify(response), 201)

api.add_resource(Users, '/users')

class UserByID(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        if user_id != current_user_id and User.query.get(current_user_id).role != 'admin':
            return make_response(jsonify({"error": "Access denied"}), 403)
        return make_response(jsonify(user.to_dict()), 200)

    @jwt_required()
    def patch(self, user_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        if user_id != current_user_id and User.query.get(current_user_id).role != 'admin':
            return make_response(jsonify({"error": "Access denied"}), 403)
        data = request.get_json()
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return make_response(jsonify(user.to_dict()), 200)

    @jwt_required()
    def delete(self, user_id):
        current_user_id = get_jwt_identity()
        if User.query.get(current_user_id).role != 'admin':
            return make_response(jsonify({"error": "Admin access required"}), 403)
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({"message": "User deleted"}), 200)

api.add_resource(UserByID, '/users/<int:user_id>')

class Flights(Resource):
    def get(self):
        flights = Flight.query.all()
        response = [flight.to_dict() for flight in flights]
        return make_response(jsonify(response), 200)

    @admin_required
    def post(self):
        data = request.get_json()
        
        # Convert date strings to datetime objects
        try:
            departure_date = datetime.fromisoformat(data['departure_date'])
            arrival_date = datetime.fromisoformat(data['arrival_date'])
        except ValueError as e:
            return make_response(jsonify({"error": "Invalid date format"}), 400)
        
        new_flight = Flight(
            flight_number=data['flight_number'],
            departure_city=data['departure_city'],
            arrival_city=data['arrival_city'],
            departure_date=departure_date,
            arrival_date=arrival_date,
            price=data['price'],
            seats_available=data['seats_available']
        )
        
        db.session.add(new_flight)
        db.session.commit()
        
        return make_response(jsonify(new_flight.to_dict()), 201)

api.add_resource(Flights, '/flights')

class FlightByID(Resource):
    def get(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        return make_response(jsonify(flight.to_dict()), 200)

    @admin_required
    def patch(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(flight, key, value)
        db.session.commit()
        return make_response(jsonify(flight.to_dict()), 200)

    @admin_required
    def delete(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        db.session.delete(flight)
        db.session.commit()
        return make_response(jsonify({"message": "Flight deleted"}), 200)

api.add_resource(FlightByID, '/flights/<int:flight_id>')

class Hotels(Resource):
    def get(self):
        hotels = Hotel.query.all()
        response = [hotel.to_dict() for hotel in hotels]
        return make_response(jsonify(response), 200)

    @admin_required
    def post(self):
        data = request.get_json()
        new_hotel = Hotel(
            name=data['name'],
            location=data['location'],
            price_per_night=data['price_per_night'],
            amenities=data.get('amenities'),
            image_url=data.get('image_url')
        )
        db.session.add(new_hotel)
        db.session.commit()
        return make_response(jsonify(new_hotel.to_dict()), 201)

api.add_resource(Hotels, '/hotels')

class HotelByID(Resource):
    def get(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        return make_response(jsonify(hotel.to_dict()), 200)

    @admin_required
    def patch(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(hotel, key, value)
        db.session.commit()
        return make_response(jsonify(hotel.to_dict()), 200)

    @admin_required
    def delete(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        db.session.delete(hotel)
        db.session.commit()
        return make_response(jsonify({"message": "Hotel deleted"}), 200)

api.add_resource(HotelByID, '/hotels/<int:hotel_id>')

class UserFlights(Resource):
    def get(self):
        user_flights = UserFlight.query.all()
        response = [user_flight.to_dict() for user_flight in user_flights]
        return make_response(jsonify(response), 200)

    @admin_required
    def post(self):
        data = request.get_json()
        new_user_flight = UserFlight(
            user_id=data['user_id'],
            flight_id=data['flight_id']
        )
        db.session.add(new_user_flight)
        db.session.commit()
        return make_response(jsonify(new_user_flight.to_dict()), 201)

api.add_resource(UserFlights, '/user_flights')

class UserFlightByID(Resource):
    def get(self, user_flight_id):
        user_flight = UserFlight.query.get_or_404(user_flight_id)
        return make_response(jsonify(user_flight.to_dict()), 200)

    @admin_required
    def delete(self, user_flight_id):
        user_flight = UserFlight.query.get_or_404(user_flight_id)
        db.session.delete(user_flight)
        db.session.commit()
        return make_response(jsonify({"message": "UserFlight deleted"}), 200)

api.add_resource(UserFlightByID, '/user_flights/<int:user_flight_id>')

class UserHotels(Resource):
    def get(self):
        user_hotels = UserHotel.query.all()
        response = [user_hotel.to_dict() for user_hotel in user_hotels]
        return make_response(jsonify(response), 200)

    @admin_required
    def post(self):
        data = request.get_json()
        new_user_hotel = UserHotel(
            user_id=data['user_id'],
            hotel_id=data['hotel_id']
        )
        db.session.add(new_user_hotel)
        db.session.commit()
        return make_response(jsonify(new_user_hotel.to_dict()), 201)

api.add_resource(UserHotels, '/user_hotels')

class UserHotelByID(Resource):
    def get(self, user_hotel_id):
        user_hotel = UserHotel.query.get_or_404(user_hotel_id)
        return make_response(jsonify(user_hotel.to_dict()), 200)

    @admin_required
    def delete(self, user_hotel_id):
        user_hotel = UserHotel.query.get_or_404(user_hotel_id)
        db.session.delete(user_hotel)
        db.session.commit()
        return make_response(jsonify({"message": "UserHotel deleted"}), 200)

api.add_resource(UserHotelByID, '/user_hotels/<int:user_hotel_id>')

class Bookings(Resource):
    def get(self):
        bookings = Booking.query.all()
        response = [booking.to_dict() for booking in bookings]
        return make_response(jsonify(response), 200)

    @admin_required
    def post(self):
        data = request.get_json()
        new_booking = Booking(
            user_id=data['user_id'],
            flight_id=data.get('flight_id'),
            hotel_id=data.get('hotel_id'),
            check_in_date=datetime.fromisoformat(data['check_in_date']),
            check_out_date=datetime.fromisoformat(data['check_out_date']),
            total_price=data['total_price']
        )
        db.session.add(new_booking)
        db.session.commit()
        return make_response(jsonify(new_booking.to_dict()), 201)

api.add_resource(Bookings, '/bookings')

class BookingByID(Resource):
    def get(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        return make_response(jsonify(booking.to_dict()), 200)

    @admin_required
    def patch(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(booking, key, value)
        db.session.commit()
        return make_response(jsonify(booking.to_dict()), 200)

    @admin_required
    def delete(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return make_response(jsonify({"message": "Booking deleted"}), 200)

api.add_resource(BookingByID, '/bookings/<int:booking_id>')



class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.user_id)
            response = {
                "token": access_token,
                "role": user.role,
                "id": user.user_id
            }
            return make_response(jsonify(response), 200)
        return make_response(jsonify({"error": "Invalid credentials"}), 401)

api.add_resource(Login, '/login/email')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
