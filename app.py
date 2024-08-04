from datetime import datetime
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Flight, Hotel, UserFlight, UserHotel, Booking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airescape.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Index(Resource):
    def get(self):
        response_dict = {"message": "Welcome to the AirEscape RESTful API"}
        return make_response(jsonify(response_dict), 200)

api.add_resource(Index, '/')

class Users(Resource):
    def get(self):
        users = User.query.all()
        response = [user.to_dict() for user in users]
        return make_response(jsonify(response), 200)

    def post(self):
        data = request.get_json()
        new_user = User(
            title=data.get('title'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            phone_number=data['phone_number']
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify(new_user.to_dict()), 201)

api.add_resource(Users, '/users')

class UserByID(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return make_response(jsonify(user.to_dict()), 200)

    def patch(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return make_response(jsonify(user.to_dict()), 200)

    def delete(self, user_id):
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

    def patch(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(flight, key, value)
        db.session.commit()
        return make_response(jsonify(flight.to_dict()), 200)

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

    def patch(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(hotel, key, value)
        db.session.commit()
        return make_response(jsonify(hotel.to_dict()), 200)

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

    def post(self):
        data = request.get_json()
        new_booking = Booking(
            user_id=data['user_id'],
            booking_date=data['booking_date'],
            total_price=data['total_price'],
            booking_type=data['booking_type'],
            booking_status=data['booking_status'],
            flight_id=data.get('flight_id'),
            hotel_id=data.get('hotel_id')
        )
        db.session.add(new_booking)
        db.session.commit()
        return make_response(jsonify(new_booking.to_dict()), 201)

api.add_resource(Bookings, '/bookings')

class BookingByID(Resource):
    def get(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        return make_response(jsonify(booking.to_dict()), 200)

    def patch(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(booking, key, value)
        db.session.commit()
        return make_response(jsonify(booking.to_dict()), 200)

    def delete(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return make_response(jsonify({"message": "Booking deleted"}), 200)

api.add_resource(BookingByID, '/bookings/<int:booking_id>')

if __name__ == '__main__':
    app.run(debug=True)
