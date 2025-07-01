# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/review_service.py
# /backend/services/review_service.py

from backend.models.InsuranceReviews import InsuranceReviews
from backend.models.InsuranceCompanies import InsuranceCompanies
from backend import db
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

class ReviewService:
    @staticmethod
    def add_review(customer_id, company_id, package_id, rating, comment=None):
        """
        Add a new review for an insurance company and package.
        """
        try:
            logger.debug(f"Adding review: customer_id={customer_id}, company_id={company_id}, package_id={package_id}, rating={rating}")

            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5.")
            if not package_id:
                raise ValueError("Package ID is required.")

            new_review = InsuranceReviews(
                customer_id=customer_id,
                company_id=company_id,
                package_id=package_id,
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

    @staticmethod
    def get_reviews_for_package(package_id):
        try:
            logger.debug(f"Fetching reviews for package_id={package_id}")
            reviews = InsuranceReviews.query.filter_by(package_id=package_id).all()
            return [{
                'customer_name': getattr(review.customer, 'customer_name', 'Unknown'),
                'rating': review.rating,
                'comment': review.comment,
                'review_date': review.review_date.strftime('%Y-%m-%d %H:%M:%S') if review.review_date else None
            } for review in reviews]
        except Exception as e:
            logger.exception(f"Error fetching reviews for package_id={package_id}: {e}")
            raise Exception(f"Failed to fetch reviews for package: {str(e)}")

    @staticmethod
    def get_reviews_by_customer(customer_id):
        try:
            logger.debug(f"Fetching reviews for customer_id={customer_id}")
            reviews = InsuranceReviews.query.filter_by(customer_id=customer_id).all()
            return [{
                'package_id': review.package_id,
                'rating': review.rating,
                'comment': review.comment,
                'review_date': review.review_date.strftime('%Y-%m-%d %H:%M:%S') if review.review_date else None
            } for review in reviews]
        except Exception as e:
            logger.exception(f"Error fetching reviews for customer_id={customer_id}: {e}")
            raise Exception(f"Failed to fetch reviews for customer: {str(e)}")

    @staticmethod
    def get_reviews_summary():
        return ReviewService.get_average_ratings()

    @staticmethod
    def get_average_ratings():
        try:
            results = (
                db.session.query(
                    InsuranceCompanies.company_id,
                    InsuranceCompanies.company_name_th.label("company_name"),
                    func.avg(InsuranceReviews.rating).label("average_rating"),
                    func.count(InsuranceReviews.review_id).label("review_count")
                )
                .join(InsuranceReviews, InsuranceReviews.company_id == InsuranceCompanies.company_id)
                .group_by(InsuranceCompanies.company_id)
                .all()
            )
            return [{
                "company_id": row.company_id,
                "company_name": row.company_name,
                "average_rating": round(row.average_rating or 0, 2),
                "review_count": row.review_count
            } for row in results]
        except Exception as e:
            logger.error(f"Error calculating average ratings: {str(e)}")
            raise Exception(f"Failed to fetch average ratings: {str(e)}")
