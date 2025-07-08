#!/usr/bin/env python3
"""
Sample vulnerable web application for testing the security agent
Contains intentional security vulnerabilities
"""

import os
import sqlite3
import hashlib
import random
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Security Issue 1: Hardcoded secret
SECRET_KEY = "super_secret_api_key_12345"
DATABASE_PASSWORD = "admin123"

class UserManager:
    def __init__(self):
        self.db_path = "users.db"
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        # Security Issue 2: SQL Injection vulnerability
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT
            )
        """)
        conn.close()
    
    def authenticate_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        # Security Issue 3: SQL Injection - direct string formatting
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor = conn.execute(query)
        user = cursor.fetchone()
        conn.close()
        return user is not None
    
    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        # Security Issue 4: More SQL injection
        query = "SELECT * FROM users WHERE id=" + str(user_id)
        cursor = conn.execute(query)
        user = cursor.fetchone()
        conn.close()
        return user
    
    def hash_password(self, password):
        # Security Issue 5: Weak hashing (MD5)
        return hashlib.md5(password.encode()).hexdigest()
    
    def generate_session_token(self):
        # Security Issue 6: Insecure random
        return str(random.random() * 1000000)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user_manager = UserManager()
    if user_manager.authenticate_user(username, password):
        token = user_manager.generate_session_token()
        return f"Login successful! Token: {token}"
    else:
        return "Login failed"

@app.route('/profile')
def profile():
    user_id = request.args.get('id')
    user_manager = UserManager()
    user = user_manager.get_user_by_id(user_id)
    
    if user:
        # Security Issue 7: XSS vulnerability
        template = f"<h1>Welcome {user[1]}!</h1><p>Email: {user[3]}</p>"
        return render_template_string(template)
    else:
        return "User not found"

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Security Issue 8: Command injection
    import subprocess
    result = subprocess.run(f"grep -r '{query}' /tmp/", shell=True, capture_output=True)
    return f"Search results: {result.stdout.decode()}"

def read_config_file(filename):
    # Security Issue 9: Path traversal
    config_path = f"/app/config/{filename}"
    try:
        with open(config_path, 'r') as f:
            return f.read()
    except:
        return None

if __name__ == '__main__':
    # Security Issue 10: Debug mode in production
    app.run(debug=True, host='0.0.0.0')
