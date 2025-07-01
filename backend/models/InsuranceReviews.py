# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/InsuranceReviews.py
from backend.models import db  # Import `db` from `__init__.py`
import logging
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# Configure Logging
logger = logging.getLogger(__name__)

class InsuranceReviews(db.Model):
    __tablename__ = 'insurance_reviews'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, ForeignKey('Customers.customer_id', ondelete="CASCADE"), nullable=False)
    package_id = db.Column(db.Integer, ForeignKey('Car_Insurance_Packages.package_id', ondelete="CASCADE"), nullable=False)
    company_id = db.Column(db.Integer, ForeignKey('Insurance_Companies.company_id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating (1-5)
    comment = db.Column(db.Text, nullable=True)  # Optional customer comment
    review_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Relationships
    customer = relationship('Customers', backref=db.backref('insurance_reviews', cascade="all, delete-orphan", lazy=True))
    package = relationship('CarInsurancePackages', backref=db.backref('insurance_reviews', cascade="all, delete-orphan", lazy=True))
    company = relationship('InsuranceCompanies', backref=db.backref('insurance_reviews', cascade="all, delete-orphan", lazy=True))

    def to_dict(self):
        """
        Convert review data to a dictionary format.
        """
        return {
            "review_id": self.review_id,
            "customer_id": self.customer_id,
            "package_id": self.package_id,
            "company_id": self.company_id,
            "rating": self.rating,
            "comment": self.comment,
            "review_date": self.review_date.strftime('%Y-%m-%d %H:%M:%S') if self.review_date else None
        }




# Functions for managing reviews
def add_review(customer_id, package_id, company_id, rating, comment=None):
    """
    Add a new review.
    """
    try:
        logger.debug(f"Adding review for customer_id={customer_id}, package_id={package_id}, company_id={company_id}, rating={rating}")

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")

        new_review = InsuranceReviews(
            customer_id=customer_id,
            package_id=package_id,
            company_id=company_id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()

        logger.info(f"Review added successfully: review_id={new_review.review_id}")
        return new_review.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error adding review: {e}")
        raise Exception(f"Failed to add review: {str(e)}")


def get_reviews_for_package(package_id):
    """
    Fetch all reviews for a specific package ID.
    """
    try:
        logger.debug(f"Fetching reviews for package_id={package_id}")
        reviews = InsuranceReviews.query.filter_by(package_id=package_id).all()

        logger.info(f"Found {len(reviews)} reviews for package_id={package_id}")
        return [review.to_dict() for review in reviews]
    except Exception as e:
        logger.exception(f"Error fetching reviews for package_id={package_id}: {e}")
        raise Exception(f"Failed to fetch reviews for package: {str(e)}")


def get_reviews_by_customer(customer_id):
    """
    Fetch all reviews by a specific customer.
    """
    try:
        logger.debug(f"Fetching reviews for customer_id={customer_id}")
        reviews = InsuranceReviews.query.filter_by(customer_id=customer_id).all()

        logger.info(f"Found {len(reviews)} reviews for customer_id={customer_id}")
        return [review.to_dict() for review in reviews]
    except Exception as e:
        logger.exception(f"Error fetching reviews for customer_id={customer_id}: {e}")
        raise Exception(f"Failed to fetch reviews for customer: {str(e)}")


def get_reviews_summary():
    """
    Fetch a summary of reviews, including average rating and review count for each company.
    """
    try:
        from sqlalchemy import func

        logger.debug("Fetching review summary grouped by company_id")
        summary = db.session.query(
            InsuranceReviews.company_id,
            func.avg(InsuranceReviews.rating).label('average_rating'),
            func.count(InsuranceReviews.review_id).label('review_count')
        ).group_by(InsuranceReviews.company_id).all()

        logger.info(f"Found review summary for {len(summary)} companies")
        return [
            {
                "company_id": item.company_id,
                "average_rating": round(item.average_rating, 2),
                "review_count": item.review_count
            }
            for item in summary
        ]
    except Exception as e:
        logger.exception("Error fetching reviews summary")
        raise Exception(f"Failed to fetch reviews summary: {str(e)}")
