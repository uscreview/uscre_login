# =========================================================
# name: main.py
# author: Weijun Li
# date: 2025-10-26
# function: JWT login
# module: Auth
# =========================================================
from dotenv import load_dotenv
load_dotenv()
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = os.getenv("PORT")
    address = os.getenv("ADDRESS")
    app.run(host=address, port=port, debug=True)
