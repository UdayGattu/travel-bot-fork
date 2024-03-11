from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Destination(Base):
    __tablename__ = 'destinations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    country = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)

    # Relationship to TravelPackages
    packages = relationship("TravelPackage", back_populates="destination")

class TravelPackage(Base):
    __tablename__ = 'travel_packages'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cost = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'))

    # Relationship to Destination
    destination = relationship("Destination", back_populates="packages")
    # Relationship to PackageDetails
    details = relationship("PackageDetail", back_populates="package")

class PackageDetail(Base):
    __tablename__ = 'package_details'

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey('travel_packages.id'))
    detail_type = Column(String(255), nullable=False) # e.g., inclusion, exclusion, etc.
    description = Column(String(1024), nullable=False)

    # Relationship to TravelPackage
    package = relationship("TravelPackage", back_populates="details")
