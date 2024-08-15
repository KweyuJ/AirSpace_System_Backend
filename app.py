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
from dotenv import load_dotenv
import os
from flask_restful import reqparse
import json
import base64
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"
app.json.compact = False

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
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
        
        
        users = User.query.all()
        response = [user.to_dict() for user in users]
        return make_response(jsonify(response), 200)
    

    def post(self):
        data = request.get_json()
        email = data['email']

        # Check if the email already exists and should add an error if it does
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
        from_city = request.args.get('from')
        to_city = request.args.get('to')
        return_date_str = request.args.get('returnDate')
        outbound_date_str = request.args.get('outboundDate')
        trip_type = request.args.get('tripType', 'oneway')  # Default to 'oneway' if not provided
        passengers = int(request.args.get('passengers', 1))

        # If no specific search parameters are provided, return all flights
        if not from_city and not to_city and not outbound_date_str:
            flights = Flight.query.all()
            response = [flight.to_dict() for flight in flights]
            return make_response(jsonify(response), 200)

        # Existing logic for filtering flights
        if not from_city or not to_city or not outbound_date_str:
            return make_response(jsonify({"error": "From, to cities, and outboundDate are required"}), 400)

        if trip_type == 'roundtrip' and not return_date_str:
            return make_response(jsonify({"error": "ReturnDate is required for roundtrip"}), 400)

        try:
            outbound_date = datetime.strptime(outbound_date_str, '%Y-%m-%d').date()
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date() if return_date_str else None
        except ValueError:
            return make_response(jsonify({"error": "Invalid date format"}), 400)

        # Query for outbound flights
        outbound_flights_query = Flight.query.filter_by(departure_city=from_city, arrival_city=to_city)
        outbound_flights_query = outbound_flights_query.filter(db.func.date(Flight.departure_date) == outbound_date)
        outbound_flights_query = outbound_flights_query.filter(Flight.seats_available >= passengers)
        outbound_flights = outbound_flights_query.all()

        response = {
            'outbound_flights': [flight.to_dict() for flight in outbound_flights]
        }

        if trip_type == 'roundtrip':
            return_flights_query = Flight.query.filter_by(departure_city=to_city, arrival_city=from_city)
            return_flights_query = return_flights_query.filter(db.func.date(Flight.departure_date) == return_date)
            return_flights_query = return_flights_query.filter(Flight.seats_available >= passengers)
            return_flights = return_flights_query.all()

            response['return_flights'] = [flight.to_dict() for flight in return_flights]

        return make_response(jsonify(response), 200)

    
    @jwt_required()
    @admin_required
    def post(self):
        data = request.get_json()

        # Validate required fields
        required_fields = [
            'flight_number', 'departure_city', 'arrival_city', 
            'departure_date', 'arrival_date', 'departure_time', 
            'arrival_time', 'price', 'seats_available'
        ]
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({"error": f"Missing field: {field}"}), 400)

        # Convert date and time strings to datetime objects
        try:
            departure_date = datetime.fromisoformat(data['departure_date'])
            arrival_date = datetime.fromisoformat(data['arrival_date'])
            departure_time = datetime.strptime(data['departure_time'], '%H:%M:%S').time()
            arrival_time = datetime.strptime(data['arrival_time'], '%H:%M:%S').time()
        except ValueError as e:
            return make_response(jsonify({"error": "Invalid date or time format"}), 400)
        
        new_flight = Flight(
            flight_number=data['flight_number'],
            departure_city=data['departure_city'],
            arrival_city=data['arrival_city'],
            departure_date=departure_date,
            arrival_date=arrival_date,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=data['price'],
            seats_available=data['seats_available'],
            trip_type=data.get('trip_type')  # Optional field
        )
        
        db.session.add(new_flight)
        db.session.commit()
        
        return make_response(jsonify(new_flight.to_dict()), 201)

api.add_resource(Flights, '/flights')

class FlightByID(Resource):
    def get(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        return make_response(jsonify(flight.to_dict()), 200)

    
    @jwt_required()
    @admin_required
    def patch(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(flight, key, value)
        db.session.commit()
        return make_response(jsonify(flight.to_dict()), 200)

    @jwt_required()
    @admin_required
    def delete(self, flight_id):
        flight = Flight.query.get_or_404(flight_id)
        db.session.delete(flight)
        db.session.commit()
        return make_response(jsonify({"message": "Flight deleted"}), 200)

api.add_resource(FlightByID, '/flights/<int:flight_id>')

class Hotels(Resource):
    def get(self):
        return jsonify([hotel.to_dict() for hotel in Hotel.query.all()])
    
    @jwt_required()
    @admin_required
    def post(self):
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'location', 'price_per_night', 'image_url', 'amenities']
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({"error": f"Missing field: {field}"}), 400)

        new_hotel = Hotel(
            name=data['name'],
            location=data['location'],
            price_per_night=data['price_per_night'],
            image_url=data['image_url'],
            amenities=data['amenities']
        )

        db.session.add(new_hotel)
        db.session.commit()

        return make_response(jsonify(new_hotel.to_dict()), 201)


api.add_resource(Hotels, '/hotels')

class HotelByID(Resource):
    def get(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        return make_response(jsonify(hotel.to_dict()), 200)

    @jwt_required()
    @admin_required
    def patch(self, hotel_id):
        hotel = Hotel.query.get_or_404(hotel_id)
        data = request.get_json()

        # Debugging: print out received data
        print(f"Received data for update: {data}")

        try:
            for key, value in data.items():
                if key in ['price_per_night']:  # Handle specific types if needed
                    setattr(hotel, key, float(value))
                else:
                    setattr(hotel, key, value)
            
            db.session.commit()
            return make_response(jsonify(hotel.to_dict()), 200)
        except Exception as e:
            print(f"Error processing update: {e}")
            db.session.rollback()  # Rollback in case of error
            return make_response(jsonify({"error": "Unable to process the update."}), 422)



    @admin_required
    def delete(self, hotel_id):
        print(f"Headers: {request.headers}")
        hotel = Hotel.query.get_or_404(hotel_id)
        try:
            db.session.delete(hotel)
            db.session.commit()
            return make_response(jsonify({"message": "Hotel deleted"}), 200)
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting hotel: {e}")
            return make_response(jsonify({"error": "Unable to delete the hotel."}), 500)

api.add_resource(HotelByID, '/hotels/<int:hotel_id>')

class UserFlights(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user_flights = UserFlight.query.filter_by(user_id=user_id).all()
        return make_response(jsonify([uf.to_dict() for uf in user_flights]), 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        new_user_flight = UserFlight(
            user_id=user_id,
            flight_id=data['flight_id']
        )
        db.session.add(new_user_flight)
        db.session.commit()
        return make_response(jsonify(new_user_flight.to_dict()), 201)

api.add_resource(UserFlights, '/user/flights')

class UserHotels(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user_hotels = UserHotel.query.filter_by(user_id=user_id).all()
        return make_response(jsonify([uh.to_dict() for uh in user_hotels]), 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        new_user_hotel = UserHotel(
            user_id=user_id,
            hotel_id=data['hotel_id']
        )
        db.session.add(new_user_hotel)
        db.session.commit()
        return make_response(jsonify(new_user_hotel.to_dict()), 201)

api.add_resource(UserHotels, '/user/hotels')

class Bookings(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        bookings = Booking.query.filter_by(user_id=user_id).all()
        return make_response(jsonify([booking.to_dict() for booking in bookings]), 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        new_booking = Booking(
            user_id=user_id,
            flight_id=data.get('flight_id'),
            hotel_id=data.get('hotel_id'),
            booking_date=datetime.utcnow()
        )
        db.session.add(new_booking)
        db.session.commit()
        return make_response(jsonify(new_booking.to_dict()), 201)

api.add_resource(Bookings, '/bookings')

# class UserInfo(Resource):
#     @jwt_required()
#     def get(self):
#         current_user_id = get_jwt_identity()
#         user = User.query.get_or_404(current_user_id)
#         return make_response(jsonify(user.to_dict()), 200)

# api.add_resource(UserInfo, '/user/info')
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

class UserProfile(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user:
            user_data = {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "name": user.name,  # Adjust according to your User model
                # Add any other fields you want to display
            }
            return jsonify(user_data)
        return make_response(jsonify({"error": "User not found"}), 404)

api.add_resource(UserProfile, '/user/profile')

def get_mpesa_token():

    consumer_key = 'YXZhAOLvjYqmX7TkAirasXHJfTjUHHqQtIOAGXYTLjjVfvUK'
    consumer_secret = 'c6SpWnqqHckfRGGGKQt56LKdwIDrMQXeHlGs9PEiSbfGLLAmnbUjc7niS8olHtJ2'

    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json()['access_token']


class MakeSTKPush(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone',
                        type=str,
                        required=True,
                        help="This field is required")

    parser.add_argument('amount',
                        type=str,
                        required=True,
                        help="This field is required")

    def post(self):
        """Make an STK push to Daraja API"""

        # get phone and amount from request body
        data = MakeSTKPush.parser.parse_args()

        # encode business_shortcode, online_passkey and current_time (yyyyMMhhmmss) to base64
        encode_data = b"<Business_shortcode><online_passkey><current timestamp>"
        passkey = base64.b64encode(encode_data)

        # make stk push
        try:
            # get access_token
            access_token = get_mpesa_token()

            # stk_push request url
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            # put access_token in request headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # define request body
            request = {
                "BusinessShortCode": "174379",
                "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3",
                "Timestamp": "20160216165627",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data["amount"],
                "PartyA": data["phone"],
                "PartyB": "174379",
                "PhoneNumber": data["phone"],
                "CallBackURL": "https://mydomain.com/pat",
                "AccountReference": "Test",
                "TransactionDesc": "Test"
            }

            # make request and catch response
            response = requests.post(api_url, json=request, headers=headers)

            # check response code for errors and return response
            if response.status_code > 299:
                return {
                    "success": False,
                    "message": "Sorry, something went wrong please try again later."
                }, 400

            
            # return a response to your user
            return {
                "data": json.loads(response.text)
            }, 200

        except:
            # catch error and return response
            return {
                "success": False,
                "message": "Sorry something went wrong please try again."
            }, 400


# stk push path [POST request to {baseURL}/stkpush]
api.add_resource(MakeSTKPush, "/stkpush")

if __name__ == '__main__':
    app.run(debug=True)
