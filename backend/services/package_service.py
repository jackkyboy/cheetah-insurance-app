# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/package_service.py
from backend.models.CarInsurancePackages import CarInsurancePackages
from backend.models.InsuranceCompanies import InsuranceCompanies
from backend import db
from sqlalchemy.orm import joinedload
from flask import request, jsonify
import logging


class PackageService:
    @staticmethod
    def get_all_packages():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        logging.debug(f"Fetching all packages: page={page}, per_page={per_page}")
        try:
            packages = CarInsurancePackages.query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            results = [PackageService.serialize_package(pkg) for pkg in packages.items]
            return jsonify({"packages": results, "total": packages.total}), 200
        except Exception as e:
            logging.exception("Error fetching all packages")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_package_by_id(package_id):
        logging.debug(f"Fetching package by ID: {package_id}")
        try:
            package = CarInsurancePackages.query.options(
                joinedload(CarInsurancePackages.company)
            ).filter_by(package_id=package_id).first()

            if not package:
                logging.warning(f"Package with ID {package_id} not found")
                return jsonify({"error": f"Package with ID {package_id} not found"}), 404

            return jsonify(PackageService.serialize_package(package)), 200
        except Exception as e:
            logging.exception(f"Error fetching package by ID {package_id}")
            return jsonify({"error": str(e)}), 500



    @staticmethod
    def search_packages(filters):
        logging.debug(f"Searching packages with filters: {filters}")
        try:
            query = CarInsurancePackages.query.options(
                joinedload(CarInsurancePackages.company)
            )

            # เพิ่มฟิลเตอร์ที่ฟอร์มส่งมา
            if filters.get("car_brand"):
                query = query.filter(CarInsurancePackages.car_brand.ilike(f"%{filters['car_brand']}%"))
            if filters.get("car_model"):
                query = query.filter(CarInsurancePackages.car_model.ilike(f"%{filters['car_model']}%"))
            if filters.get("car_submodel"):
                query = query.filter(CarInsurancePackages.car_submodel.ilike(f"%{filters['car_submodel']}%"))

            # ✅ ปรับ filter ประเภทประกันภัย
            insurance_type = filters.get("insurance_type")
            if insurance_type:
                if isinstance(insurance_type, list):
                    query = query.filter(CarInsurancePackages.insurance_type.in_(insurance_type))
                else:
                    query = query.filter(CarInsurancePackages.insurance_type == insurance_type)

            if filters.get("repair_type"):
                query = query.filter(CarInsurancePackages.repair_type == filters["repair_type"])
            if filters.get("premium_min") is not None:
                query = query.filter(CarInsurancePackages.premium >= filters["premium_min"])
            if filters.get("premium_max") is not None:
                query = query.filter(CarInsurancePackages.premium <= filters["premium_max"])

            # Pagination
            page = max(filters.get("page", 1), 1)
            per_page = max(filters.get("per_page", 10), 1)
            logging.debug(f"Pagination Parameters: page={page}, per_page={per_page}")

            packages = query.paginate(page=page, per_page=per_page, error_out=False)

            # Serialize Results
            results = [PackageService.serialize_package(pkg) for pkg in packages.items]
            logging.info(f"Found {len(results)} packages. Total: {packages.total}")

            return jsonify({"packages": results, "total": packages.total}), 200
        except Exception as e:
            logging.exception("Error searching packages")
            return jsonify({"error": "An error occurred while searching packages.", "details": str(e)}), 500



    @staticmethod
    def add_package(data):
        required_fields = ["company_id", "car_submodel", "premium"]
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            new_package = CarInsurancePackages(
                company_id=data["company_id"],
                car_submodel=data["car_submodel"],
                premium=data["premium"],
                cmi_amount=data.get("cmi_amount", 0),
                liability_per_person=data.get("liability_per_person", 0),
                liability_per_event=data.get("liability_per_event", 0),
                liability_property=data.get("liability_property", 0),
                liability_deductible=data.get("liability_deductible", 0),
                own_damage=data.get("own_damage", 0),
                own_theft_fire_damage=data.get("own_theft_fire_damage", 0),
                coverage_driver_death=data.get("coverage_driver_death", 0),
                coverage_passenger_death=data.get("coverage_passenger_death", 0),
                coverage_medical_expense=data.get("coverage_medical_expense", 0),
                coverage_bail_bond=data.get("coverage_bail_bond", 0),
                repair_type=data.get("repair_type", "N/A"),
            )
            db.session.add(new_package)
            db.session.commit()
            logging.info("Package added successfully")
            return jsonify(PackageService.serialize_package(new_package)), 201
        except Exception as e:
            db.session.rollback()
            logging.exception("Error adding package")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def update_package(package_id, data):
        logging.debug(f"Updating package with ID: {package_id}")
        package = CarInsurancePackages.query.filter_by(package_id=package_id).first()
        if not package:
            logging.warning(f"Package with ID {package_id} not found")
            return jsonify({"error": f"Package with ID {package_id} not found"}), 404

        try:
            for key, value in data.items():
                if hasattr(package, key):
                    setattr(package, key, value)
            db.session.commit()
            logging.info(f"Package with ID {package_id} updated successfully")
            return jsonify(PackageService.serialize_package(package)), 200
        except Exception as e:
            db.session.rollback()
            logging.exception("Error updating package")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def delete_package(package_id):
        logging.debug(f"Deleting package with ID: {package_id}")
        package = CarInsurancePackages.query.filter_by(package_id=package_id).first()
        if not package:
            logging.warning(f"Package with ID {package_id} not found")
            return jsonify({"error": f"Package with ID {package_id} not found"}), 404

        try:
            db.session.delete(package)
            db.session.commit()
            logging.info(f"Package with ID {package_id} deleted successfully")
            return jsonify({"message": f"Package with ID {package_id} deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logging.exception("Error deleting package")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def serialize_package(package):
        """ แปลง Object เป็น JSON """
        return {
            "package_id": package.package_id,
            "company_name": package.company.company_name if package.company else "N/A",
            "car_brand": package.car_brand or "ไม่ระบุ",
            "car_model": package.car_model or "ไม่ระบุ",
            "car_submodel": package.car_submodel or "ไม่ระบุ",
            "car_model_year": package.car_model_year or "ไม่ระบุ",
            "insurance_type": package.insurance_type or "ไม่ระบุ",
            "repair_type": package.repair_type or "ไม่ระบุ",
            "premium": package.premium or 0,
            "cmi_amount": package.cmi_amount if package.cmi_amount is not None else "ไม่ระบุ",
            "liability_per_person": package.liability_per_person if package.liability_per_person is not None else "ไม่ระบุ",
            "liability_per_event": package.liability_per_event if package.liability_per_event is not None else "ไม่ระบุ",
            "liability_property": package.liability_property if package.liability_property is not None else "ไม่ระบุ",
            "liability_deductible": package.liability_deductible if package.liability_deductible is not None else "ไม่ระบุ",
            "own_damage": package.own_damage if package.own_damage is not None else "ไม่ระบุ",
            "own_theft_fire_damage": package.own_theft_fire_damage if package.own_theft_fire_damage is not None else "ไม่ระบุ",
            "coverage_medical_expense": package.coverage_medical_expense if package.coverage_medical_expense is not None else "ไม่ระบุ",
            "coverage_bail_bond": package.coverage_bail_bond if package.coverage_bail_bond is not None else "ไม่ระบุ",
        }