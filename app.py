from flask import Flask, jsonify, send_from_directory
import json
import os
from flask_cors import CORS
from flask import request
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 🔥 use service role key to allow inserts
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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


@app.route("/api/update", methods=["POST"])
def update_profiles():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != os.getenv("API_SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    new_data = request.json
    if not isinstance(new_data, list):
        return jsonify({"error": "Invalid payload"}), 400

    added = 0
    for item in new_data:
        # check if profile_url exists already
        existing = supabase.table("profiles").select("id").eq("profile_url", item["profile_url"]).execute()
        if not existing.data:
            supabase.table("profiles").insert(item).execute()
            added += 1

    return jsonify({"status": "success", "added": added})




@app.route("/api/profiles")
def get_profiles():
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {secret_token}":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        res = supabase.table("profiles").select("*").order("created_at", desc=True).limit(100).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
