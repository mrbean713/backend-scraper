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
OUTPUT_FILE = "scraper/output.json"
CORS(app, resources={r"/api/*": {"origins": "https://recruitment-dashboard-ten.vercel.app"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"])



# ✅ Protect this route with your token
@app.route("/api/update", methods=["POST"])
def update_profiles():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != os.getenv("API_SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    new_data = request.json
    if not isinstance(new_data, list):
        return jsonify({"error": "Invalid payload"}), 400

    try:
        # Load existing data
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r") as f:
                existing = json.load(f)
        else:
            existing = []

        # Filter out duplicates
        existing_urls = {d["profile_url"] for d in existing}
        combined = existing + [item for item in new_data if item["profile_url"] not in existing_urls]

        # Save back to file
        with open(OUTPUT_FILE, "w") as f:
            json.dump(combined, f, indent=2)

        return jsonify({"status": "success", "added": len(combined) - len(existing)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    print("🛂 Login route hit")
    body = request.json
    agency = body.get("agency")
    password = body.get("password")
    if valid_credentials.get(agency) == password:
        return jsonify({"status": "ok"})
    return jsonify({"error": "invalid credentials"}), 401

@app.route('/')
def home():
    return '✅ Backend is live!'



if __name__ == '__main__':
    print("🚀 Starting Flask backend on http://localhost:5050")
    app.run(debug=True, port=5050)
