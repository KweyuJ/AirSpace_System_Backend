from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)
 
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(10), nullable=True,)
    first_name =db.Column(db.String(50), unique=True, nullable=False)
    last_name =db. Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    
    flights = db.relationship('UserFlight', back_populates='user')
    hotels = db.relationship('UserHotel', back_populates='user')
    bookings = db.relationship('Booking', back_populates='user')

    
    
    @validates('email')
    def validate_email(self, key, email):
        # Simple regex for validating an Email
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(regex, email):
            raise ValueError("Invalid email address")
        return email

    def _repr_(self):
        return f'<User {self.id}, {self.username}, {self.email}, {self.role}>'

class Flight(db.Model, SerializerMixin):
    __tablename__ = 'flights'
    flight_id =db.Column(db.Integer, primary_key=True, unique=True)
    flight_number =db.Column(db.String, nullable=False, unique=True)
    departure_city =db.Column(db.String, nullable=False)
    arrival_city =db.Column(db.String, nullable=False)
    departure_date =db.Column(db.DateTime, nullable=False)
    arrival_date =db.Column(db.DateTime, nullable=False)
    price =db.Column(db.Float, nullable=False)
    seats_available =db.Column(db.Integer, nullable=False)
    
    user_flights = db.relationship('UserFlight', back_populates='flight')
    bookings = db.relationship('Booking', back_populates='flight')
    
    def __repr__(self):
        return f'<Flight {self.flight_id}, {self.flight_number}>'

class Hotel(db.Model, SerializerMixin):
    __tablename__ = 'hotels'
    hotel_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    amenities = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    
    user_hotels = db.relationship('UserHotel', back_populates='hotel')
    bookings = db.relationship('Booking', back_populates='hotel')
    
    def __repr__(self):
        return f'<Hotel {self.hotel_id}, {self.name}, {self.location}>'
 
class UserHotel(db.Model, SerializerMixin):
    __tablename__ = 'user_hotels'
    user_hotel_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id'), nullable=False)
    
    user = db.relationship('User', back_populates='hotels')
    hotel = db.relationship('Hotel', back_populates='user_hotels')
    
    def __repr__(self):
        return f'<UserHotel{self.user_hotel_id}, {self.user_id}, {self.hotel_id}>'
    
class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_type = db.Column(db.String, nullable=False)  
    booking_status = db.Column(db.String, nullable=False)  
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.flight_id'), nullable=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id'), nullable=True)
    
    user = db.relationship('User', back_populates='bookings')
    flight = db.relationship('Flight', back_populates='bookings')
    hotel = db.relationship('Hotel', back_populates='bookings')
    
    def __repr__(self):
        return f'<Booking{self.booking_id}, {self.user_id}, {self.total_price}, {self.booking_type}, {self.booking_status}>'