from backend.models.InsuranceCompanies import InsuranceCompanies
from backend import db
from datetime import datetime, timedelta


class InsuranceCompanyService:
    @staticmethod
    def create_company(company_name, api_endpoint, api_token=None, token_expiration=None):
        """
        สร้างบริษัทประกันภัยใหม่
        """
        if InsuranceCompanies.query.filter_by(company_name=company_name).first():
            raise ValueError("Insurance company already exists.")

        try:
            company = InsuranceCompanies(
                company_name=company_name,
                api_endpoint=api_endpoint,
                api_token=api_token,
                token_expiration=token_expiration
            )
            db.session.add(company)
            db.session.commit()
            return company
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating insurance company: {str(e)}")

    @staticmethod
    def update_company(company_id, updates):
        """
        อัปเดตข้อมูลบริษัทประกันภัย
        """
        company = InsuranceCompanies.query.get(company_id)
        if not company:
            raise ValueError("Insurance company not found.")

        try:
            for key, value in updates.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            db.session.commit()
            return company
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating company: {str(e)}")

    @staticmethod
    def get_company_by_id(company_id):
        """
        ดึงข้อมูลบริษัทประกันภัยโดยใช้ company_id
        """
        company = InsuranceCompanies.query.get(company_id)
        if not company:
            raise ValueError("Insurance company not found.")
        return company

    @staticmethod
    def get_all_companies():
        """
        ดึงข้อมูลบริษัทประกันภัยทั้งหมด
        """
        try:
            return InsuranceCompanies.query.all()
        except Exception as e:
            raise Exception(f"Error fetching companies: {str(e)}")

    @staticmethod
    def get_valid_api_token(company_id):
        """
        ตรวจสอบและดึง Token ของบริษัทประกันภัย
        """
        company = InsuranceCompanies.query.get(company_id)
        if not company:
            raise ValueError("Insurance company not found.")

        # ตรวจสอบว่า Token หมดอายุหรือไม่
        if not company.api_token or (company.token_expiration and company.token_expiration < datetime.utcnow()):
            # เรียกฟังก์ชันเพื่อรีเฟรช Token
            new_token, new_expiration = InsuranceCompanyService.refresh_api_token(company.api_endpoint)
            company.api_token = new_token
            company.token_expiration = new_expiration
            company.last_token_refresh = datetime.utcnow()
            db.session.commit()

        return company.a
