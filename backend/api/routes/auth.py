# auth.py (Flask authentication logic)
import json
import os
from datetime import datetime
from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = os.path.join("backend", "api", "routes", "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        print("⚠️ users.json does not exist.")
        return []
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        print(f"✅ Loaded {len(users)} users from {USERS_FILE}")
        return users  # ✅ return the already loaded data

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_routes(app):

    @app.route("/signup", methods=["POST", "OPTIONS"])
    def signup():
        if request.method == "OPTIONS":
            # Handle preflight CORS request
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        users = load_users()
        if any(u["username"] == username for u in users):
            return jsonify({"error": "User already exists"}), 400

        hashed_pw = generate_password_hash(password)
        new_user = {
            "username": username, 
            "password": hashed_pw, 
            "role": "admin" if username == "admin" else "user",
            "created_at": datetime.now().isoformat(),
            "email": f"{username}@example.com",
            "last_login": None
        }

        users.append(new_user)
        save_users(users)
        return jsonify({"message": "✅ User registered"}), 200

    @app.route("/login", methods=["POST", "OPTIONS"])
    def login():
        if request.method == "OPTIONS":
            # Handle preflight CORS request
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Update last login time
        user["last_login"] = datetime.now().isoformat()
        save_users(users)
        
        # Make session permanent and set user data
        session.permanent = True
        session["user"] = {
            "username": user["username"], 
            "role": user["role"],
            "email": user.get("email", f"{user['username']}@example.com")
        }
        return jsonify({"message": "✅ Logged in", "user": session["user"]}), 200

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("user", None)
        return jsonify({"message": "Logged out"})

    @app.route("/me", methods=["GET"])
    def me():
        user = session.get("user")
        if not user:
            return jsonify({"error": "Not logged in"}), 401
        return jsonify(user)

    @app.route("/admin/users", methods=["GET"])
    def get_all_users():
        """Admin-only endpoint to view all user accounts"""
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        users = load_users()
        # Don't send password hashes to frontend
        safe_users = []
        for u in users:
            safe_user = {
                "username": u["username"],
                "role": u["role"],
                "email": u.get("email", "N/A"),
                "created_at": u.get("created_at", "N/A"),
                "last_login": u.get("last_login", "Never")
            }
            safe_users.append(safe_user)
        
        return jsonify(safe_users), 200

    @app.route("/admin/users/<username>", methods=["DELETE"])
    def delete_user(username):
        """Admin-only endpoint to delete user accounts"""
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        
        if username == "admin":
            return jsonify({"error": "Cannot delete admin user"}), 400

        users = load_users()
        users = [u for u in users if u["username"] != username]
        save_users(users)
        
        return jsonify({"message": f"User {username} deleted successfully"}), 200

    @app.route("/admin/users/<username>/role", methods=["PUT"])
    def update_user_role(username):
        """Admin-only endpoint to update user roles"""
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        data = request.get_json()
        new_role = data.get("role")
        
        if new_role not in ["user", "admin"]:
            return jsonify({"error": "Invalid role"}), 400

        users = load_users()
        target_user = next((u for u in users if u["username"] == username), None)
        if not target_user:
            return jsonify({"error": "User not found"}), 404

        target_user["role"] = new_role
        save_users(users)
        
        return jsonify({"message": f"User {username} role updated to {new_role}"}), 200
