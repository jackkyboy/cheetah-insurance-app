# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/decode_secrets.py
import os, base64

def decode_env_to_file(env_var, out_path):
    val = os.getenv(env_var)
    if not val:
        raise ValueError(f"Missing env var: {env_var}")
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(val))

# ใช้ tmp path ตอน runtime
decode_env_to_file("SANDBOX_PKCS7_BASE64", "/tmp/sandbox-pkcs7.cer")
decode_env_to_file("PRIVATE_KEY_BASE64", "/tmp/merchant-private-key.der")
decode_env_to_file("PUBLIC_CERT_BASE64", "/tmp/jwt-demo.cer")
decode_env_to_file("GOOGLE_CREDENTIALS_BASE64", "/tmp/credentials.json")

# สำหรับ Google Lib
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
