from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sqlite3
import csv
import io

app = Flask(__name__)
CORS(app)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        electricity REAL,
        travel REAL,
        waste REAL,
        total_carbon REAL,
        category TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    electricity = float(data.get("electricity", 0))
    travel = float(data.get("travel", 0))
    waste = float(data.get("waste", 0))

    total_carbon = round((electricity * 0.5 + travel * 0.2 + waste * 0.1), 2)

    if total_carbon < 100:
        category = "Low"
    elif total_carbon < 300:
        category = "Moderate"
    else:
        category = "High"

    # Save to database
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO entries (electricity, travel, waste, total_carbon, category)
           VALUES (?, ?, ?, ?, ?)''',
        (electricity, travel, waste, total_carbon, category)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "totalCarbon": total_carbon,
        "category": category
    })

@app.route('/export', methods=['GET'])
def export_data():
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Electricity", "Travel", "Waste", "Total Carbon", "Category"])
    writer.writerows(rows)
    output.seek(0)

    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=carbon_submissions.csv"})

if __name__ == "__main__":
    app.run(debug=True)

