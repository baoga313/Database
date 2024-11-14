from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db import engine

# Create the base class for the ORM
Base = declarative_base()

# Define the Guest model
class Guest(Base):
    __tablename__ = 'Guest'

    # Columns for guest table
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(15))

# Define the Room model
class Room(Base):
    __tablename__ = 'Room'

    # Columns for room table
    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    price_per_night = Column(DECIMAL(10, 2))
    capacity = Column(Integer)

# Define the Reservation model
class Reservation(Base):
    __tablename__ = 'Reservation'

    # Columns for the reservation table
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey('Guest.id'))
    payment_status = Column(String(100), nullable=False)
    guest = relationship("Guest", back_populates="reservations")

# Define the relationship between reservation and guest
Guest.reservations = relationship("Reservation", order_by=Reservation.id, back_populates="guest")

# Define the RoomReservation model
class RoomReservation(Base):
    __tablename__ = 'Room_reservation'

    # Columns for room_reservation table
    reservation_id = Column(Integer, ForeignKey('Reservation.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('Room.id'), primary_key=True)
    check_in_date = Column(Date)
    check_out_date = Column(Date)
    status = Column(Enum('Reserved', 'Check-in', 'Checked-out', 'Cancelled'), nullable=False)

# Define the Vehicles model
class Vehicle(Base):
    __tablename__ = 'Vehicles'

    # Columns definition for the Vehicles table
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    brand = Column(String(50))
    color = Column(String(40))
    room_id = Column(Integer, ForeignKey('Room.id'))

# Define the Payment model
class Payment(Base):
    __tablename__ = 'Payment'

    # Columns for Payment table
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey('Reservation.id'))
    payment_method = Column(Enum('Credit Card', 'PayPal', 'Cash', 'Debit Card'))
    status = Column(String(50))
    payment_date = Column(Date)

# Create tables if they don't exist
Base.metadata.create_all(engine)
