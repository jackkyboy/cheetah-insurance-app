# /Users/apichet/Downloads/cheetah-insurance-app/utils/logging_config.py
import logging

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("cheetah-insurance-app")

# สร้าง logger
logger = configure_logging()
