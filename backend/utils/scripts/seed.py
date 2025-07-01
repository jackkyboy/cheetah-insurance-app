from app import app, db
from backend.models import Customers, Users, InsuranceCompanies, CarInsurancePackages, Coupons


def seed_data():
    with app.app_context():
        try:
            # สร้าง InsuranceCompanies
            company1 = InsuranceCompanies(
                company_name="Insurance Co. A",
                api_base_url="https://api.insurancea.com",
                api_token="token123",
                agent_code="AGENT001",
                partner_code="PARTNER001"
            )
            db.session.add(company1)

            # สร้าง Customers
            customer1 = Customers(
                customer_name="John Doe",
                contact_info="johndoe@example.com"
            )
            db.session.add(customer1)
            db.session.flush()  # บันทึกข้อมูลชั่วคราวเพื่อให้ใช้งาน FK ได้

            # สร้าง Users ที่เกี่ยวข้องกับ Customers
            user1 = Users(
                customer_id=customer1.customer_id,  # FK เชื่อมกับ customer_id
                email="johndoe@example.com",
                password_hash=generate_password_hash("password123")
            )
            db.session.add(user1)

            # สร้าง CarInsurancePackages
            package1 = CarInsurancePackages(
                company_id=company1.company_id,  # FK เชื่อมกับ company_id
                car_submodel="Toyota Corolla",
                premium=1200.00,
                cmi_amount=500.00
            )
            db.session.add(package1)

            # สร้าง Coupons
            coupon1 = Coupons(
                code="DISCOUNT10",
                discount_percentage=10.0,
                expiration_date="2024-12-31"
            )
            db.session.add(coupon1)

            db.session.commit()
            print("Seed data added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding data: {str(e)}")


if __name__ == "__main__":
    seed_data()
