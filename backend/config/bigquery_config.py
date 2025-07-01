# /Users/apichet/Downloads/cheetah-insurance-app/backend/config/bigquery_config.py
from google.cloud import bigquery
import os
import logging

# ตั้งค่าการบันทึก (Logging)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BigQueryConfig:
    def __init__(self):
        """
        Initialize the BigQueryConfig and set up the BigQuery client with asia-southeast1 location.
        """
        self.client = self._initialize_client()

    @staticmethod
    def _initialize_client():
        """
        Initialize the BigQuery client by checking the credentials and setting up the environment.
        Forces location to 'asia-southeast1'
        """
        try:
            # ✅ Force path to local credentials file (explicit path)
            credentials_path = "/Users/apichet/Downloads/cheetah-insurance-app/backend/config/credentials.json"

            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"❌ Credentials file not found at {credentials_path}")

            # ✅ Set environment variable if not already set
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") != credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                logger.debug(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to {credentials_path}")

            # ✅ Initialize client with correct region
            client = bigquery.Client(location="asia-southeast1")
            logger.info("✅ BigQuery client created successfully in asia-southeast1.")
            return client

        except Exception as e:
            logger.error(f"❌ Error initializing BigQuery client: {e}")
            raise RuntimeError("Failed to initialize BigQuery client. Check your configuration.")

    def run_query(self, query, parameters=None):
        """
        Run a BigQuery SQL query with optional parameters.

        :param query: (str) SQL query
        :param parameters: (list of bigquery.ScalarQueryParameter)
        :return: Query result as RowIterator
        """
        if not self.client:
            raise RuntimeError("BigQuery client is not initialized.")

        try:
            logger.debug(f"🚀 Running BigQuery query:\n{query}")
            if parameters:
                logger.debug(f"📦 Parameters: {parameters}")

            job_config = bigquery.QueryJobConfig(query_parameters=parameters or [])
            query_job = self.client.query(query, job_config=job_config)
            result = query_job.result()
            logger.info(f"✅ Query executed successfully. Rows: {result.total_rows}")
            return result

        except Exception as e:
            logger.error(f"❌ Error executing BigQuery query: {e}", exc_info=True)
            raise RuntimeError(f"BigQuery query execution failed: {e}")

# 🔧 Global instance (use only if absolutely needed)
bigquery_config = BigQueryConfig()
