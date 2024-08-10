from app import app
from models import db, User, Flight, Hotel, Booking, UserFlight, UserHotel
from datetime import datetime, time

with app.app_context():

    print("Deleting data...")
    UserFlight.query.delete()
    UserHotel.query.delete()
    Booking.query.delete()
    Flight.query.delete()
    Hotel.query.delete()
    User.query.delete()

    print("Creating users...")
    user1 = User(first_name="Alice", last_name="Johnson", email="alice@example.com", password="password", role="traveler", phone_number="1234567890")
    user2 = User(first_name="Bob", last_name="Smith", email="bob@example.com", password="password", role="traveler", phone_number="0987654321")
    user3 = User(first_name="Admin", last_name="User", email="admin@example.com", password="password", role="admin", phone_number="1122334455")
    users = [user1, user2, user3]

    print("Creating flights...")
    flights = [
    Flight(flight_number="AA123", departure_city="Nairobi", arrival_city="Kisumu", departure_date=datetime(2024, 8, 15), arrival_date=datetime(2024, 8, 15), departure_time=time(10, 0), arrival_time=time(11, 0), price=7420, seats_available=10, trip_type="oneway"),
    Flight(flight_number="BA456", departure_city="Mombasa", arrival_city="Nairobi", departure_date=datetime(2024, 9, 10), arrival_date=datetime(2024, 9, 10), departure_time=time(9, 0), arrival_time=time(10, 0), price=7000, seats_available=80, trip_type="roundtrip"),
    Flight(flight_number="CA789", departure_city="Eldoret", arrival_city="Nairobi", departure_date=datetime(2024, 10, 5), arrival_date=datetime(2024, 10, 5), departure_time=time(8, 0), arrival_time=time(9, 0), price=8025, seats_available=6, trip_type="oneway"),
    Flight(flight_number="DA321", departure_city="Nairobi", arrival_city="Mombasa", departure_date=datetime(2024, 11, 20), arrival_date=datetime(2024, 11, 20), departure_time=time(7, 0), arrival_time=time(8, 0), price=9940, seats_available=12, trip_type="oneway"),
    Flight(flight_number="EA654", departure_city="Kisumu", arrival_city="Nairobi", departure_date=datetime(2024, 12, 1), arrival_date=datetime(2024, 12, 1), departure_time=time(6, 0), arrival_time=time(7, 0), price=9560, seats_available=12, trip_type="roundtrip"),
    Flight(flight_number="FA987", departure_city="Nairobi", arrival_city="Eldoret", departure_date=datetime(2024, 12, 10), arrival_date=datetime(2024, 12, 10), departure_time=time(5, 0), arrival_time=time(6, 0), price=6999, seats_available=7, trip_type="oneway"),
    Flight(flight_number="GA123", departure_city="Mombasa", arrival_city="Kisumu", departure_date=datetime(2024, 12, 15), arrival_date=datetime(2024, 12, 15), departure_time=time(4, 0), arrival_time=time(5, 0), price=7500, seats_available=5, trip_type="roundtrip"),
    Flight(flight_number="HA456", departure_city="Kisumu", arrival_city="Eldoret", departure_date=datetime(2024, 12, 20), arrival_date=datetime(2024, 12, 20), departure_time=time(3, 0), arrival_time=time(4, 0), price=8175, seats_available=9, trip_type="oneway"),
    Flight(flight_number="IA789", departure_city="Eldoret", arrival_city="Mombasa", departure_date=datetime(2024, 12, 25), arrival_date=datetime(2024, 12, 25), departure_time=time(2, 0), arrival_time=time(3, 0), price=7999, seats_available=50, trip_type="roundtrip"),
    Flight(flight_number="JA321", departure_city="Nairobi", arrival_city="Nakuru", departure_date=datetime(2024, 12, 30), arrival_date=datetime(2024, 12, 30), departure_time=time(1, 0), arrival_time=time(2, 0), price=6400, seats_available=11, trip_type="oneway"),
    Flight(flight_number="KA654", departure_city="Nakuru", arrival_city="Nairobi", departure_date=datetime(2024, 12, 31), arrival_date=datetime(2024, 12, 31), departure_time=time(0, 0), arrival_time=time(1, 0), price=6740, seats_available=15, trip_type="roundtrip"),
]


    print("Creating hotels...")
    hotels = [
        Hotel(name="Southern Palms Beach Resort", image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/221320289.jpg?k=1203f024f73c994f979bc9aea38a85e531a038f988994c1681df935203e83845&o=&hp=1", location="Diani Beach Road Diani, Ukunda", price_per_night=25000, amenities="2 outdoor swimming pools, Free on-site parking, Air conditioning, Private Bathroom, Free Wifi, Room service, Family rooms, 5 restaurants, Breakfast, Spa, Gym"),
        Hotel(name="Kilili Baharini Resort & Spa", image_url="https://www.kililibaharini.com/wp-content/uploads/2019/11/mainpool-slide.jpg", location="Casuarina Road, Malindi, Kenya", price_per_night=18000, amenities="Beach Access, Free Breakfast, Gym, Free Parking"),
        Hotel(name="Hemingways Watamu", image_url="https://www.shadesofafricasafaris.com/images/hemingways-watamu4.jpg", location="Watamu, Kenya", price_per_night=15000, amenities="2 swimming pools, Free Wifi, Beachfront, Family rooms, Airport shuttle, Restaurant, Fitness center, Tea/Coffee Maker in All Rooms, Bar, Breakfast, Free Breakfast"),
        Hotel(name="Mnarani Beach Club", image_url="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2b/61/9a/9d/caption.jpg?w=700&h=-1&s=1", location="Kilifi, Kenya", price_per_night=15000, amenities="Free WiFi, Gym, Valet Parking, Restaurant"),
        Hotel(name="Movenpick Hotel & Residences Nairobi", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoJx9UPSgJCe-qvNHQ0bVD3U6oX5NI-be40A&s", location="Nairobi, Kenya", price_per_night=29000, amenities="Free WiFi, Bowling offsite, Airport shuttle, Chapel/shrine, Sauna, Fitness center Gym, Tea/coffee maker in all rooms, Free Parking"),
        Hotel(name="Villa Rosa Kempinski Nairobi", image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/43569297.jpg?k=1cb33050f9949454276dc0b61159c39405baaf58b823b4c1201136894efefb7f&o=&hp=1", location="Chiromo Road, Nairobi, Kenya", price_per_night=25000, amenities="9 treatment rooms, a lounge area for relaxing after treatments, a jacuzzi, sauna, steam room, heated swimming pool, and well-equipped gym."),
        Hotel(name="Sarova Imperial Kisumu", image_url="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/27/57/9b/66/imperial-hotel.jpg?w=700&h=-1&s=1", location="Achieng' Oneko Rd, Kisumu", price_per_night=15000, amenities="Free WiFi, Airport shuttle, Fitness center Gym, Facilities for disabled guests, Tea/coffee maker in all rooms, Free Parking"),
        Hotel(name="Eka Hotel, Eldoret", image_url="https://tembeatujengekenya.com/wp-content/uploads/2022/05/DJI_0968.jpg", location="Eldoret, Kenya", price_per_night=13000, amenities="TV with DSTV connection, complimentary high-speed Wi-fi, minibar, safety deposit box, coffee/tea making facilities, telephone, hair dryers and Iron/Ironing boards on request, bathroom with toiletries."),
        Hotel(name="Lake Nakuru Lodge", image_url="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1a/bf/51/8f/lake-nakuru-lodge.jpg?w=500&h=-1&s=1", location="Lake Nakuru National Park, Kenya", price_per_night=10000, amenities="Free WiFi, seating area and flat-screen TV. There is a private bathroom with bath and free toiletries in each unit, along with a hair dryer."),
        Hotel(name="Little Governors' Camp", image_url="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2b/33/57/d6/caption.jpg?w=700&h=-1&s=1", location="Maasai Mara National Reserve, Kenya", price_per_night=30000, amenities="A restaurant, 2 bars/lounges, and dry cleaning are available at this campground. Free buffet breakfast, free WiFi in public areas, and free self parking are also provided. Additionally, laundry facilities, wedding services, and a garden are onsite. The accommodation features a furnished patio, room service, and free bottled water. Amenities also include a shower and free toiletries."),
        Hotel(name="The Majlis Resort", image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/263081767.jpg?k=c2fc50d5eff98ac2f4d7f8eeec1ce289c651aa1e681d4de75c9ef124da0a8873&o=&hp=1", location="Lamu, Kenya", price_per_night=15000, amenities="Free WiFi, Airport shuttle, Fitness center Gym, minibar, air conditioning and safe, Tea/coffee maker in all rooms, Free Parking"),
        Hotel(name="Enashipai Resort & Spa", image_url="https://media-cdn.tripadvisor.com/media/photo-s/12/50/82/63/aerial-view-of-enashipai.jpg", location="Moi S Lake Rd, Naivasha", price_per_night=12000, amenities="Free WiFi, Airport shuttle, Fitness center Gym, minibar, air conditioning and safe, Tea/coffee maker in all rooms, Free Parking")
    ]

    print("Creating bookings...")
    bookings = [
        Booking(user=user1, booking_date=datetime.now(), total_price=1000.00, booking_type="flight", booking_status="confirmed", flight=flights[0]),
        Booking(user=user2, booking_date=datetime.now(), total_price=1500.00, booking_type="hotel", booking_status="pending", hotel=hotels[0])
    ]

    print("Creating user flights...")
    user_flights = [
        UserFlight(user=user1, flight=flights[0]),
        UserFlight(user=user2, flight=flights[1]),
        UserFlight(user=user1, flight=flights[2]),
        UserFlight(user=user2, flight=flights[3])
    ]

    print("Creating user hotels...")
    user_hotels = [
        UserHotel(user=user1, hotel=hotels[0]),
        UserHotel(user=user2, hotel=hotels[1]),
        UserHotel(user=user1, hotel=hotels[2]),
        UserHotel(user=user2, hotel=hotels[3])
    ]

    print("Adding data to the database...")
    db.session.add_all(users)
    db.session.add_all(flights)
    db.session.add_all(hotels)
    db.session.add_all(bookings)
    db.session.add_all(user_flights)
    db.session.add_all(user_hotels)
    db.session.commit()
    print("Data added successfully.")

   