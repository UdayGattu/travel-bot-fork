# from sqlalchemy import Boolean,Column, Integer,String
# from database import Base

# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer,primary_key=True,index=True)
#     username = Column(String(50),unique=True)

# class Post(Base):
#     __tablename__='posts'
#     id =Column(Integer,primary_key=True,index=True)
#     title = Column(String(50))
#     content = Column(String(100))
#     user_id = Column(Integer)
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    country = Column(String(255))
    timezone = Column(String(255))
    airports = relationship("Airport", back_populates="city")  # Relationship to Airports

class Airport(Base):
    __tablename__ = "airports"
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    name = Column(String(255))
    iata_code = Column(String(255), unique=True)
    city = relationship("City", back_populates="airports")  # Relationship back to City

class Flight(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, index=True)
    departure_airport_id = Column(Integer, ForeignKey('airports.id'))
    arrival_airport_id = Column(Integer, ForeignKey('airports.id'))
    flight_duration = Column(Float)  # Flight duration in hours or minutes
    operating_airlines = Column(String(255))
    departure_airport = relationship("Airport", foreign_keys=[departure_airport_id])
    arrival_airport = relationship("Airport", foreign_keys=[arrival_airport_id])

class TravelPackage(Base):
    __tablename__ = "travel_packages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(400))
    cost = Column(Float)
    origin_city_id = Column(Integer, ForeignKey('cities.id'))
    destination_city_id = Column(Integer, ForeignKey('cities.id'))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    origin_city = relationship("City", foreign_keys=[origin_city_id])
    destination_city = relationship("City", foreign_keys=[destination_city_id])
