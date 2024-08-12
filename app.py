from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # Initialize CORS

# Secret key for encoding/decoding JWT tokens
app.config['SECRET_KEY'] = 'companykey'

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

# Dummy OAuth2 token storage (for demonstration purposes)
access_tokens = {}

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
            # Create JWT token with expiration time
            expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            token = jwt.encode({
                'sub': username,
                'exp': expiration
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            # Store token in a simple dict (for demonstration purposes)
            access_tokens[username] = token
            
            return jsonify({
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 1800  # Token expiration time in seconds (30 minutes)
            })

    # If invalid credentials
    return jsonify({"error": "Invalid credentials"}), 401

# Middleware to verify token
@app.before_request
def verify_token():
    if request.endpoint == 'oauth_token':
        return  # Skip token verification for the token endpoint
    
    token = request.headers.get('Authorization')
    if token:
        try:
            token = token.split(' ')[1]  # Remove "Bearer" prefix
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        return jsonify({"error": "Token required"}), 401



if __name__ == "__main__":
    app.run(debug=True)