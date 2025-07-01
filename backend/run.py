# /Users/apichet/Downloads/cheetah-insurance-app/backend/run.py
import os
import sys

# Ensure that backend directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ✅ Import create_app from backend package
from backend import create_app

# ✅ Create app instance
app = create_app()

# ✅ Run app only when executed directly
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
