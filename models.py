from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import re


metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(10), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    
    flights = db.relationship('UserFlight', back_populates='user', cascade="all, delete-orphan")
    hotels = db.relationship('UserHotel', back_populates='user', cascade="all, delete-orphan")
    bookings = db.relationship('Booking', back_populates='user', cascade="all, delete-orphan")

    @validates('email')
    def validate_email(self, key, email):
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(regex, email):
            raise ValueError("Invalid email address")
        return email

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if value and (len(value) < 10 or len(value) > 15):
            raise ValueError("Phone number must be between 10 and 15 characters")
        return value

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'phone_number': self.phone_number,

            'flights': [uf.to_dict() for uf in self.flights],
            'hotels': [uh.to_dict() for uh in self.hotels],
            'bookings': [b.to_dict() for b in self.bookings]
        }

    def __repr__(self):
        return f'<User {self.user_id}, {self.first_name}, {self.email}, {self.role}>'
class Flight(db.Model, SerializerMixin):
    __tablename__ = 'flights'
    
    flight_id = db.Column(db.Integer, primary_key=True, unique=True)
    flight_number = db.Column(db.String, nullable=False, unique=True)
    departure_city = db.Column(db.String, nullable=False)
    arrival_city = db.Column(db.String, nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    trip_type = db.Column(db.String(10), nullable=False)  # New field

    user_flights = db.relationship('UserFlight', back_populates='flight', cascade="all, delete-orphan")
    bookings = db.relationship('Booking', back_populates='flight', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'flight_id': self.flight_id,
            'flight_number': self.flight_number,
            'departure_city': self.departure_city,
            'arrival_city': self.arrival_city,
            'departure_date': self.departure_date.isoformat() if self.departure_date else None,
            'arrival_date': self.arrival_date.isoformat() if self.arrival_date else None,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'price': self.price,
            'seats_available': self.seats_available,
            'trip_type': self.trip_type,
            'user_flights': [uf.to_dict() for uf in self.user_flights],
            'bookings': [b.to_dict() for b in self.bookings]
        }

    def __repr__(self):
        return f'<Flight {self.flight_id}, {self.flight_number}, {self.trip_type}>'



class Hotel(db.Model, SerializerMixin):
    __tablename__ = 'hotels'
    
    hotel_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    amenities = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    
    user_hotels = db.relationship('UserHotel', back_populates='hotel', cascade="all, delete-orphan")
    bookings = db.relationship('Booking', back_populates='hotel', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'hotel_id': self.hotel_id,
            'name': self.name,
            'location': self.location,
            'price_per_night': self.price_per_night,
            'amenities': self.amenities,
            'image_url': self.image_url,
            
            'user_hotels': [uh.to_dict() for uh in self.user_hotels],
            'bookings': [b.to_dict() for b in self.bookings]
        }

    def __repr__(self):
        return f'<Hotel {self.hotel_id}, {self.name}, {self.location}>'

class UserFlight(db.Model, SerializerMixin):
    __tablename__ = 'user_flights'
    
    user_flight_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.flight_id'), nullable=False)
    
    user = db.relationship('User', back_populates='flights')
    flight = db.relationship('Flight', back_populates='user_flights')

    def to_dict(self):
        return {
            'user_flight_id': self.user_flight_id,
            'user_id': self.user_id,
            'flight_id': self.flight_id
            
        }

    def __repr__(self):
        return f'<UserFlight {self.user_flight_id}, {self.user_id}, {self.flight_id}>'

class UserHotel(db.Model, SerializerMixin):
    __tablename__ = 'user_hotels'
    
    user_hotel_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id'), nullable=False)
    
    user = db.relationship('User', back_populates='hotels')
    hotel = db.relationship('Hotel', back_populates='user_hotels')

    def to_dict(self):
        return {
            'user_hotel_id': self.user_hotel_id,
            'user_id': self.user_id,
            'hotel_id': self.hotel_id
            
        }

    def __repr__(self):
        return f'<UserHotel {self.user_hotel_id}, {self.user_id}, {self.hotel_id}>'

class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    booking_type = db.Column(db.String, nullable=False)
    booking_status = db.Column(db.String, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.flight_id'), nullable=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id'), nullable=True)
    
    user = db.relationship('User', back_populates='bookings')
    flight = db.relationship('Flight', back_populates='bookings')
    hotel = db.relationship('Hotel', back_populates='bookings')

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'total_price': self.total_price,
            'booking_type': self.booking_type,
            'booking_status': self.booking_status,
            'flight_id': self.flight_id,
            'hotel_id': self.hotel_id
            
        }

    def __repr__(self):
        return f'<Booking {self.booking_id}, {self.user_id}, {self.total_price}, {self.booking_type}, {self.booking_status}>'
