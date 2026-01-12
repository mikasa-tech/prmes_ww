
from waitress import serve
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    print(f"Starting production server on http://{host}:{port}")
    serve(app, host=host, port=port)
