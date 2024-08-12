from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Initialize CORS

# Load users from JSON file
def load_users():
    with open('users.json') as f:
        return json.load(f)
    
    # Dummy OAuth2 token
access_tokens = {"admin_token": "admin"}

# Root API
@app.route("/")
def hello_world():
    return "<h2>Welcome to Companies Flask API !</h2>"

# Login API
@app.route("/oauth/token", methods=["POST"])
def oauth_token():
    # Extract client credentials from request
    username = request.json.get("username")
    password = request.json.get("password")
    
    users = load_users().get("users", [])
    
    # Validate user credentials
    for user in users:
        if user["username"] == username and user["password"] == password:
            # Return OAuth2 token
            return jsonify({
                "access_token": access_tokens.get(f"{username}_token"),
                "token_type": "Bearer"
            })

    # If invalid credentials
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)