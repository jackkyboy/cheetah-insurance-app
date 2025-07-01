# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/__init__.py
import logging

# Import all service modules
try:
    from backend.services.auth_services import AuthService
    from backend.services.bigquery_service import BigQueryService
    from backend.services.document_service import DocumentService
    from backend.services.admin_service import AdminService 
    from backend.services.payment_service import PaymentService
    from backend.services.policy_service import PolicyService
    from backend.services.review_service import ReviewService
    from backend.services.uploaded_documents_service import UploadedDocumentsService
    from backend.services.coupon_service import CouponService
    from backend.services.claim_service import ClaimService
    from backend.services.package_service import PackageService
    from backend.services.customer_info_service import CustomerInfoService
    from backend.services.gateway_2c2p import Gateway2C2P
    from backend.services.insurance_preparation_service import InsurancePreparationService
    from backend.services.ollama_service import askOllamaWithData, parseOllamaToPackages
    from backend.config.bigquery_config import BigQueryConfig
except ImportError as e:
    logging.error(f"❌ Service import failed: {e}")
    raise ImportError(f"Service module failed to load: {e}")

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
def init_services(app):
    logger.info("🔧 Initializing services...")

    app.config["CUSTOM_SETTING"] = "value"
    app.extensions = getattr(app, "extensions", {})

    # ✅ Define services with constructor injection if needed
    services = {
        "admin_service": AdminService,
        "auth_service": AuthService,
        "bigquery_service": lambda: BigQueryService(
            project_id="cheetah-insurance-broker",
            location="asia-southeast1"
        ),
        "document_service": DocumentService,
        "payment_service": PaymentService,
        "policy_service": PolicyService,
        "review_service": ReviewService,
        "uploaded_documents_service": UploadedDocumentsService,
        "coupon_service": CouponService,
        "claim_service": ClaimService,
        "package_service": PackageService,
        "customer_info_service": CustomerInfoService,
        "gateway_2c2p": Gateway2C2P,
        "insurance_preparation_service": InsurancePreparationService,
        # เปลี่ยนตรงนี้: ollama_service เป็นคลาส (ไม่ต้องใส่วงเล็บ)
        "ollama_service": OllamaService,
    }

    initialized_services = []
    failed_services = []

    for key, service_factory in services.items():
        try:
            # ถ้า service_factory เป็น callable (เช่นคลาสหรือ lambda) ให้เรียกสร้าง instance
            instance = service_factory() if callable(service_factory) else service_factory
            app.extensions[key] = instance
            initialized_services.append(key)
            logger.info(f"✅ Service initialized: {key}")
        except Exception as e:
            app.extensions[key] = None
            failed_services.append(key)
            logger.error(f"❌ Failed to initialize {key}: {e}", exc_info=True)

    if initialized_services:
        logger.info(f"✅ Successfully initialized services: {', '.join(initialized_services)}")
    if failed_services:
        logger.warning(f"⚠️ Failed to initialize services: {', '.join(failed_services)}")

    for key in initialized_services:
        logger.debug(f"Initialized service: {key} -> {app.extensions[key]}")

    # Log a summary of successfully initialized services
    if initialized_services:
        logger.info(f"✅ Successfully initialized services: {', '.join(initialized_services)}")
    else:
        logger.warning("⚠️ No services were successfully initialized.")

    # Log a summary of failed services
    if failed_services:
        logger.warning(f"⚠️ Failed to initialize services: {', '.join(failed_services)}")

    # Debugging: Print out initialized services
    for key in initialized_services:
        logger.debug(f"Initialized service: {key} -> {app.extensions[key]}")



