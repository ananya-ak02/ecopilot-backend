from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import csv
import os

app = Flask(__name__)
CORS(app)

# --- DB Setup ---
DB_NAME = 'submissions.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            carbon_footprint REAL NOT NULL,
            suggestions TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Main Submission Route ---
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        carbon = data.get('carbonFootprint')
        suggestions = data.get('suggestions', '')

        if not name or not email or carbon is None:
            return jsonify({"error": "Missing required fields"}), 400

        if float(carbon) < 0:
            return jsonify({"error": "Carbon footprint cannot be negative"}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (name, email, carbon_footprint, suggestions)
            VALUES (?, ?, ?, ?)
        ''', (name, email, carbon, suggestions))
        conn.commit()
        conn.close()

        return jsonify({"message": "Submission saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Export CSV Route ---
@app.route('/export', methods=['GET'])
def export_csv():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM submissions')
        rows = cursor.fetchall()
        conn.close()

        csv_file = 'submissions_export.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Email', 'Carbon Footprint', 'Suggestions'])
            writer.writerows(rows)

        return send_file(csv_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- HackRx Webhook ---
@app.route('/hackrx/run', methods=['POST'])
def hackrx_run():
    try:
        data = request.get_json()

        # Simulate a simple response or processing
        response = {
            "status": "success",
            "message": "Received your HackRx test request.",
            "echo": data  # Echo back the input for testing
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True)

