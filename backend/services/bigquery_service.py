# /Users/apichet/Downloads/cheetah-insurance-app/services/bigquery_service.py
from google.cloud import bigquery
from google.api_core.exceptions import NotFound, BadRequest
import logging
import os

class BigQueryService:
    def __init__(self, project_id, location):
        """
        Initialize the BigQueryService with the specified project ID and location.
        """
        credentials_path = "/Users/apichet/Downloads/cheetah-insurance-app/backend/config/credentials.json"
        if not os.path.exists(credentials_path):
            logging.error(f"Credentials file not found: {credentials_path}")
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") != credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logging.debug(f"GOOGLE_APPLICATION_CREDENTIALS set to {credentials_path}")

        try:
            self.client = bigquery.Client(project=project_id, location=location)
            logging.debug("BigQuery Client initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize BigQuery Client: {str(e)}")
            raise RuntimeError(f"Error initializing BigQuery Client: {str(e)}")

    def execute_query_with_count(self, query, parameters):
        """
        Execute a single query that returns both data and total row count.
        """
        try:
            job_config = bigquery.QueryJobConfig(query_parameters=parameters)
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            rows = [dict(row) for row in results]
            if not rows:
                return {"message": "No data found for the given criteria"}, 200

            # Map company names to Thai
            for row in rows:
                row['company_name_th'] = self.map_company_name_to_thai(row.get('company_name'))

            total_rows = rows[0].get('total_rows', 0)
            return {"data": rows, "total_rows": total_rows}, 200

        except BadRequest as e:
            logging.error(f"BadRequest Error: {str(e)}")
            return {"error": "Invalid query or parameters"}, 400
        except NotFound as e:
            logging.error(f"NotFound Error: {str(e)}")
            return {"error": "Table or data not found"}, 404
        except Exception as e:
            logging.error(f"Unexpected Error: {str(e)}")
            return {"error": "An unexpected error occurred"}, 500

    @staticmethod
    def map_company_name_to_thai(company_name):
        """
        Map company name to its Thai equivalent.
        """
        company_mapping = {
            "Ergo": "บริษัท เออร์โกประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
            "Chubb": "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)",
            "Tokio Marine": "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
            "Viriyah": "บริษัท วิริยะประกันภัย จำกัด (มหาชน)",
            "MTI": "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)",
        }
        return company_mapping.get(company_name, "Unknown Company")

    def execute_query(self, query: str, parameters: list = None) -> list:
        """
        Execute a BigQuery query and return results as list of dicts.
        """
        try:
            job_config = bigquery.QueryJobConfig()
            if parameters:
                job_config.query_parameters = parameters

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            return [dict(row) for row in results]

        except BadRequest as e:
            logging.error(f"BadRequest Error in execute_query: {str(e)}")
            raise
        except NotFound as e:
            logging.error(f"NotFound Error in execute_query: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in execute_query: {str(e)}")
            raise
