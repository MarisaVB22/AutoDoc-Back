from app import app

from app.config.config import APP_PORT # Puerto 5000

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT, debug=True)