import openai
from google.cloud import bigquery
import os
import logging

# ✅ ตั้งค่า API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ✅ ตั้งค่า Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ✅ ใช้ global ตัวเดียวให้คลาสอื่น reuse
bigquery_client = None

def get_bigquery_client():
    """
    ใช้ Singleton Pattern ป้องกันการสร้าง BigQuery Client ซ้ำซ้อน
    """
    global bigquery_client
    if bigquery_client is None:
        try:
            bigquery_client = bigquery.Client(project="cheetah-insurance-broker")  # 🔧 แก้ตรงนี้
            logger.debug("✅ BigQuery client created for project: cheetah-insurance-broker")
        except Exception as e:
            logger.error(f"❌ Failed to create BigQuery client: {e}")
            raise
    return bigquery_client


def query_bigquery(user_query):
    """
    🔍 ค้นหาข้อมูลจาก BigQuery
    ✅ ถ้ามีข้อมูล → ใช้ข้อมูลนี้ตอบ
    ❌ ถ้าไม่มีข้อมูล → ให้ GPT-4 ตอบแทน
    """
    try:
        client = get_bigquery_client()
        query = """
        SELECT response_text FROM `cheetah-insurance-broker.chatbot_responses`
        WHERE LOWER(question) LIKE @user_query
        LIMIT 1
        """
        query_params = [
            bigquery.ScalarQueryParameter("user_query", "STRING", f"%{user_query.lower()}%")
        ]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        for row in results:
            return row["response_text"]
        return None
    except Exception as e:
        logger.error(f"❌ Error querying BigQuery: {e}")
        return None


def get_chatbot_response(user_query):
    """
    ✅ ถ้ามีข้อมูลใน BigQuery → ใช้ข้อมูลนี้
    ❌ ถ้าไม่มี → ใช้ GPT-4 ช่วยตอบ
    """
    bigquery_response = query_bigquery(user_query)
    if bigquery_response:
        return bigquery_response

    # 🧠 ถ้าไม่มี → ใช้ GPT-4 สร้างคำตอบ
    prompt = f"""
    ผู้ใช้ถามเกี่ยวกับประกันภัย: "{user_query}"
    กรุณาตอบคำถามให้กระชับ ชัดเจน และถูกต้อง
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "คุณเป็น AI ที่ช่วยตอบคำถามเกี่ยวกับเบี้ยประกันภัย."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return "ขออภัย ฉันไม่สามารถตอบคำถามนี้ได้ในขณะนี้"


def train_chatbot(question, response):
    """
    ✅ เพิ่มข้อมูลเข้า BigQuery เพื่อให้ Chatbot ฉลาดขึ้นเรื่อยๆ
    """
    try:
        client = get_bigquery_client()
        query = """
        INSERT INTO `cheetah-insurance-broker.chatbot_responses` (question, response_text)
        VALUES (@question, @response)
        """
        query_params = [
            bigquery.ScalarQueryParameter("question", "STRING", question.lower()),
            bigquery.ScalarQueryParameter("response", "STRING", response),
        ]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Execute the query

        logger.info(f"✅ Training Data Added: {question} → {response}")
        return True
    except Exception as e:
        logger.error(f"❌ Error inserting training data: {e}")
        return False
