from google.cloud import bigquery
import time
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/apichet/Downloads/cheetah-insurance-app/backend/config/credentials.json"

client = bigquery.Client()

def run_query():
    try:
        start_time = time.time()

        QUERY = """
        SELECT
            Insurance_company,
            car_brand,
            car_model,
            car_submodel,
            car_model_year,
            insurance_type,
            premium,
            repair_type
        FROM
            `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE
            car_brand = @car_brand
            AND car_model_year = @car_model_year
            AND car_model = @car_model
            AND insurance_type = @insurance_type
        LIMIT 10
        """

        parameters = [
            bigquery.ScalarQueryParameter("car_brand", "STRING", "Toyota"),
            bigquery.ScalarQueryParameter("car_model_year", "STRING", "2022"),
            bigquery.ScalarQueryParameter("car_model", "STRING", "Camry"),
            bigquery.ScalarQueryParameter("insurance_type", "STRING", "Comprehensive"),
        ]

        job_config = bigquery.QueryJobConfig(
            query_parameters=parameters,
            use_query_cache=True  # Enable caching
        )

        query_job = client.query(QUERY, job_config=job_config)
        results = list(query_job.result())

        end_time = time.time()
        print(f"Query Results: {len(results)} rows retrieved")
        print(f"Time Taken: {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error: {e}")

run_query()

