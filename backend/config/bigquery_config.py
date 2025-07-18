# /Users/apichet/Downloads/cheetah-insurance-app/backend/config/bigquery_config.py
# /backend/config/bigquery_config.py

import os
import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BigQueryConfig:
    def __init__(self):
        self.client = None

    def initialize_client(self):
        """
        Initialize BigQuery client with credentials from GOOGLE_APPLICATION_CREDENTIALS.
        Forces location to 'asia-southeast1'.
        """
        try:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            logger.debug(f"[DEBUG] GOOGLE_APPLICATION_CREDENTIALS={credentials_path}")

            if not credentials_path or not os.path.isfile(credentials_path):
                raise FileNotFoundError(
                    f"❌ GOOGLE_APPLICATION_CREDENTIALS is not set or file does not exist: {credentials_path}"
                )

            logger.debug(f"✅ Using credentials: {credentials_path}")
            self.client = bigquery.Client(location="asia-southeast1")
            logger.info("✅ BigQuery client initialized (asia-southeast1)")

        except Exception as e:
            logger.error(f"❌ Error initializing BigQuery client: {e}", exc_info=True)
            raise RuntimeError("Failed to initialize BigQuery client.")

    def run_query(self, query, parameters=None):
        if not self.client:
            raise RuntimeError("BigQuery client is not initialized. Call `initialize_client()` first.")

        try:
            logger.debug(f"🚀 Executing query:\n{query}")
            if parameters:
                logger.debug(f"📦 Parameters: {parameters}")

            job_config = bigquery.QueryJobConfig(query_parameters=parameters or [])
            result = self.client.query(query, job_config=job_config).result()

            logger.info(f"✅ Query executed: {result.total_rows} rows returned")
            return result

        except Exception as e:
            logger.error(f"❌ Query failed: {e}", exc_info=True)
            raise RuntimeError(f"BigQuery query failed: {e}")
