# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CarInfo.py
from backend.db import (
    db, Model, Column, Integer, String, ForeignKey, DateTime, relationship
)
import logging

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CarInfo(Model):
    """
    Represents information about a customer's car.
    """
    __tablename__ = 'CarInfo'

    car_id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key for CarInfo table")
    car_brand = Column(String(100), nullable=False, comment="Brand of the car (e.g., Honda)")
    car_model = Column(String(100), nullable=False, comment="Model of the car (e.g., Civic)")
    car_year = Column(String(4), nullable=False, comment="Year the car was manufactured")
    car_submodel = Column(String(100), nullable=True, comment="Submodel of the car (optional)")
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False, comment="Foreign key to Customers table")

    customer = relationship('Customers', back_populates='car_info', lazy='joined')

    def to_dict(self):
        logger.debug(f"Converting CarInfo ID {self.car_id} to dictionary.")
        return {
            'car_id': self.car_id,
            'car_brand': self.car_brand,
            'car_model': self.car_model,
            'car_year': self.car_year,
            'car_submodel': self.car_submodel,
            'customer_id': self.customer_id
        }



# Service Functions

def add_car_info(customer_id, car_brand, car_model, car_year, car_submodel=None):
    """
    Adds a new car record to the database for a specified customer.

    Args:
        customer_id (int): ID of the customer to whom the car belongs.
        car_brand (str): The brand of the car.
        car_model (str): The model of the car.
        car_year (str): The year the car was manufactured.
        car_submodel (str, optional): The submodel of the car.

    Returns:
        dict: A dictionary representation of the added car.
    """
    try:
        logger.debug(f"Adding car info for customer_id={customer_id}: {car_brand} {car_model} {car_year}")
        new_car = CarInfo(
            customer_id=customer_id,
            car_brand=car_brand,
            car_model=car_model,
            car_year=car_year,
            car_submodel=car_submodel
        )
        db.session.add(new_car)
        db.session.commit()
        logger.info(f"Car added successfully with ID {new_car.car_id}")
        return new_car.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error adding car information.")
        raise Exception(f"Error adding car information: {str(e)}")


def get_cars_by_customer(customer_id):
    """
    Retrieves all cars associated with a specific customer.

    Args:
        customer_id (int): The ID of the customer.

    Returns:
        list: A list of dictionaries, each representing a car.
    """
    try:
        logger.debug(f"Fetching cars for customer_id={customer_id}")
        cars = CarInfo.query.filter_by(customer_id=customer_id).all()
        if not cars:
            logger.warning(f"No cars found for customer_id={customer_id}")
            return []
        logger.info(f"Retrieved {len(cars)} cars for customer_id={customer_id}")
        return [car.to_dict() for car in cars]
    except Exception as e:
        logger.exception("Error fetching car information.")
        raise Exception(f"Error fetching car information: {str(e)}")


def update_car(car_id, **kwargs):
    """
    Updates car details in the database.

    Args:
        car_id (int): The ID of the car to be updated.
        kwargs: Key-value pairs representing fields to update.

    Returns:
        dict: The updated car details.
    """
    try:
        logger.debug(f"Updating car info with ID {car_id}")
        car = CarInfo.query.get(car_id)
        if not car:
            logger.warning(f"Car not found with ID {car_id}")
            raise ValueError("Car not found")

        # Update the fields
        for key, value in kwargs.items():
            if hasattr(car, key) and value is not None:
                setattr(car, key, value)

        db.session.commit()
        logger.info(f"Car updated successfully with ID {car_id}")
        return car.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error updating car information.")
        raise Exception(f"Error updating car information: {str(e)}")


def delete_car(car_id):
    """
    Deletes a car record from the database.

    Args:
        car_id (int): The ID of the car to delete.

    Returns:
        dict: Confirmation message upon successful deletion.
    """
    try:
        logger.debug(f"Deleting car with ID {car_id}")
        car = CarInfo.query.get(car_id)
        if not car:
            logger.warning(f"Car not found with ID {car_id}")
            raise ValueError("Car not found")
        db.session.delete(car)
        db.session.commit()
        logger.info(f"Car deleted successfully with ID {car_id}")
        return {"message": "Car deleted successfully"}
    except Exception as e:
        db.session.rollback()
        logger.exception("Error deleting car.")
        raise Exception(f"Error deleting car: {str(e)}")
