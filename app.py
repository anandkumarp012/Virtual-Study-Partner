from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["virtual_study_partner"]
users_collection = db["users"]
courses_collection = db["courses"]
playlists_collection = db["playlists"]
teachers_collection = db["teachers"]

# User Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    # Validate input data
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"message": "User already exists"}), 400
    
    # Hash password before storing
    hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    data["password"] = hashed_password.decode("utf-8")
    
    try:
        users_collection.insert_one(data)
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error registering user", "error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    # Validate input data
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    user = users_collection.find_one({"email": data["email"]})
    
    if user and bcrypt.checkpw(data["password"].encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"message": "Login successful", "user": {"email": user["email"], "name": user.get("name")}}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

# Course Routes
@app.route("/courses", methods=["GET"])
def get_courses():
    try:
        courses = list(courses_collection.find({}, {"_id": 0}))
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": "Error fetching courses", "error": str(e)}), 500

@app.route("/courses", methods=["POST"])
def add_course():
    data = request.json

    # Validate input data
    if not data.get("title") or not data.get("description"):
        return jsonify({"message": "Title and description are required"}), 400

    try:
        courses_collection.insert_one(data)
        return jsonify({"message": "Course added successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error adding course", "error": str(e)}), 500

# Playlist Routes
@app.route("/playlists", methods=["GET"])
def get_playlists():
    try:
        playlists = list(playlists_collection.find({}, {"_id": 0}))
        return jsonify(playlists), 200
    except Exception as e:
        return jsonify({"message": "Error fetching playlists", "error": str(e)}), 500

@app.route("/playlists", methods=["POST"])
def add_playlist():
    data = request.json

    # Validate input data
    if not data.get("name") or not data.get("description"):
        return jsonify({"message": "Name and description are required"}), 400

    try:
        playlists_collection.insert_one(data)
        return jsonify({"message": "Playlist added successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error adding playlist", "error": str(e)}), 500

# Teacher Routes
@app.route("/teachers", methods=["GET"])
def get_teachers():
    try:
        teachers = list(teachers_collection.find({}, {"_id": 0}))
        return jsonify(teachers), 200
    except Exception as e:
        return jsonify({"message": "Error fetching teachers", "error": str(e)}), 500

@app.route("/teachers", methods=["POST"])
def add_teacher():
    data = request.json

    # Validate input data
    if not data.get("name") or not data.get("subject"):
        return jsonify({"message": "Name and subject are required"}), 400

    try:
        teachers_collection.insert_one(data)
        return jsonify({"message": "Teacher profile added successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error adding teacher profile", "error": str(e)}), 500

# Update User Profile
@app.route("/update-profile", methods=["PUT"])
def update_profile():
    data = request.json
    email = data.get("email")
    update_fields = {k: v for k, v in data.items() if k != "email"}
    
    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        result = users_collection.update_one({"email": email}, {"$set": update_fields})
        if result.modified_count > 0:
            return jsonify({"message": "Profile updated successfully"}), 200
        return jsonify({"message": "No changes made or user not found"}), 400
    except Exception as e:
        return jsonify({"message": "Error updating profile", "error": str(e)}), 500

# Watch Video Route
@app.route("/watch-video", methods=["POST"])
def watch_video():
    data = request.json

    # Validate input data
    if not data.get("video_title"):
        return jsonify({"message": "Video title is required"}), 400

    # Handle video watching logic here (mocked for now)
    response = {"message": f"You are watching: {data.get('video_title', 'Unknown')}"}
    return jsonify(response), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(debug=True)