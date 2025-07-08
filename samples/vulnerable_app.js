/**
 * Sample vulnerable Node.js application for testing the security agent
 * Contains intentional security vulnerabilities
 */

const express = require('express');
const mysql = require('mysql');
const crypto = require('crypto');

const app = express();

// Security Issue 1: Hardcoded credentials
const API_KEY = "sk-1234567890abcdef";
const DB_PASSWORD = "root123";

// Security Issue 2: Insecure database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: DB_PASSWORD,
    database: 'myapp'
});

class AuthService {
    constructor() {
        this.sessions = new Map();
    }

    // Security Issue 3: SQL Injection vulnerability
    authenticateUser(username, password, callback) {
        const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
        db.query(query, (error, results) => {
            if (error) {
                callback(error, null);
                return;
            }
            callback(null, results.length > 0);
        });
    }

    // Security Issue 4: More SQL injection
    getUserById(userId) {
        return new Promise((resolve, reject) => {
            const query = "SELECT * FROM users WHERE id = " + userId;
            db.query(query, (error, results) => {
                if (error) reject(error);
                else resolve(results[0]);
            });
        });
    }

    // Security Issue 5: Weak session token generation
    generateSessionToken() {
        return Math.random().toString(36).substring(2);
    }

    // Security Issue 6: Insecure password hashing
    hashPassword(password) {
        return crypto.createHash('md5').update(password).digest('hex');
    }
}

// Security Issue 7: XSS vulnerability in template
app.get('/user/:id', async (req, res) => {
    const userId = req.params.id;
    const authService = new AuthService();
    
    try {
        const user = await authService.getUserById(userId);
        if (user) {
            // Direct HTML injection without escaping
            const html = `<h1>Welcome ${user.name}!</h1><p>Bio: ${user.bio}</p>`;
            res.send(html);
        } else {
            res.status(404).send('User not found');
        }
    } catch (error) {
        res.status(500).send('Database error');
    }
});

// Security Issue 8: Command injection
app.get('/logs/:filename', (req, res) => {
    const filename = req.params.filename;
    const { exec } = require('child_process');
    
    // Dangerous command execution
    exec(`cat /var/log/${filename}`, (error, stdout, stderr) => {
        if (error) {
            res.status(500).send('Error reading log file');
            return;
        }
        res.send(`<pre>${stdout}</pre>`);
    });
});

// Security Issue 9: Eval usage
app.post('/calculate', (req, res) => {
    const expression = req.body.expression;
    try {
        // Never use eval with user input!
        const result = eval(expression);
        res.json({ result: result });
    } catch (error) {
        res.status(400).json({ error: 'Invalid expression' });
    }
});

// Security Issue 10: Path traversal
app.get('/files/:filename', (req, res) => {
    const filename = req.params.filename;
    const fs = require('fs');
    const path = `/app/uploads/${filename}`;
    
    try {
        const content = fs.readFileSync(path, 'utf8');
        res.send(content);
    } catch (error) {
        res.status(404).send('File not found');
    }
});

// Security Issue 11: Unsafe innerHTML usage (client-side)
function updateUserProfile(userData) {
    const profileDiv = document.getElementById('profile');
    // XSS vulnerability
    profileDiv.innerHTML = `
        <h2>${userData.name}</h2>
        <p>Email: ${userData.email}</p>
        <p>About: ${userData.about}</p>
    `;
}

// Security Issue 12: No input validation
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const authService = new AuthService();
    
    authService.authenticateUser(username, password, (error, isValid) => {
        if (error) {
            res.status(500).json({ error: 'Database error' });
            return;
        }
        
        if (isValid) {
            const token = authService.generateSessionToken();
            res.json({ success: true, token: token });
        } else {
            res.status(401).json({ error: 'Invalid credentials' });
        }
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
