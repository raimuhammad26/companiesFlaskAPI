from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import jwt
import datetime
import os

app = Flask(__name__)
CORS(app)  # Initialize CORS

# Secret key for encoding/decoding JWT tokens
app.config['SECRET_KEY'] = 'companykey'

# Load users from JSON file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json') as f:
            return json.load(f)
    return {"users": []}
    
# Dummy OAuth2 token
access_tokens = {"admin_token": "admin"}

# Save users to JSON file Function
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Root API
@app.route("/")
def hello_world():
    return "<h2>Welcome to Companies Flask API !</h2>"

# Dummy OAuth2 token storage (for demonstration purposes)
access_tokens = {}


# Sign-Up API
@app.route("/signup", methods=["POST"])
def signup():
    # Extract user details from request
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    print(username)
    print(password)
    
    users_data = load_users()
    users = users_data.get("users", [])
    
    # Check if username already exists
    for user in users:
        if user["username"] == username:
            return jsonify({"error": "Username already exists"}), 400
        
    # Add new user
    users.append({
        "username": username,
        "password": password  # In a real application, hash the password before saving
    })
    save_users({"users": users})
    
    return jsonify({"message": "User created successfully"}), 201


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

# Company List API
@app.route('/company_list', methods=['GET'])
def company_list():
    # Load the JSON file
    with open('companies.json', 'r') as file:
        data = json.load(file)
    
    # Return the companies as a JSON response
    return jsonify(data)

# Middleware to verify token
@app.before_request
def verify_token():
    if request.endpoint in ['oauth_token', 'signup', 'hello_world', 'company_list']:
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