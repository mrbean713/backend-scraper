from flask import Flask, jsonify, send_from_directory
import json
import os
from flask_cors import CORS
from flask import request

secret_token = os.getenv("API_SECRET_TOKEN")
valid_credentials = {
    os.getenv("AGENCY_1"): os.getenv("PASSWORD_1"),
    os.getenv("AGENCY_2"): os.getenv("PASSWORD_2")
}


app = Flask(__name__, static_folder='static')
CORS(app, origins=["https://recruitment-dashboard-ten.vercel.app/"])

@app.route('/api/profiles')
def get_profiles():
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {secret_token}":
        print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401
    try:
        file_path = 'scraper/output.json'
        if not os.path.exists(file_path):
            print("⚠️ output.json not found.")
            return jsonify([])

        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                print("⚠️ output.json is empty.")
                return jsonify([])

            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSONDecodeError: {e}")
                return jsonify([])

        return jsonify(data)

    except Exception as e:
        print(f"❌ Unexpected error in /api/profiles: {e}")
        return jsonify([])

@app.route('/static/profile_pics/<path:filename>')
def serve_profile_pic(filename):
    return send_from_directory('scraper/static/profile_pics', filename)

@app.route("/api/login", methods=["POST"])
def login():
    body = request.json
    agency = body.get("agency")
    password = body.get("password")
    if valid_credentials.get(agency) == password:
        return jsonify({"status": "ok"})
    return jsonify({"error": "invalid credentials"}), 401


if __name__ == '__main__':
    print("🚀 Starting Flask backend on http://localhost:5050")
    app.run(debug=True, port=5050)
