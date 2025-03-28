import os
from flask import Flask, request, jsonify, render_template, redirect
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_PATH = os.path.join(BASE_DIR, 'data.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lon REAL,
            comment TEXT,
            image TEXT,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            created_at TEXT,
            user_id TEXT,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_point', methods=['POST'])
def add_point():
    lat = request.form['lat']
    lon = request.form['lon']
    comment = request.form['comment']
    user_id = request.form.get('user_id', 'anonymous')
    username = request.form.get('username', '—')
    image_file = request.files.get('image')
    image_path = ''
    if image_file:
        filename = secure_filename(image_file.filename)
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(saved_path)
        image_path = f'/static/uploads/{filename}'
    created_at = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO points (lat, lon, comment, image, created_at, user_id, username) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (lat, lon, comment, image_path, created_at, user_id, username))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/get_points')
def get_points():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM points")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/admin')
def admin():
    secret = request.args.get("secret")
    if secret != "nalchik2025":
        return "Access denied", 403
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM points ORDER BY created_at DESC")
    points = c.fetchall()
    conn.close()
    return render_template("admin.html", points=points)

@app.route('/delete_point/<int:point_id>', methods=['POST'])
def delete_point(point_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM points WHERE id = ?", (point_id,))
    conn.commit()
    conn.close()
    return redirect("/admin?secret=nalchik2025")

@app.route('/like_point/<int:point_id>', methods=['POST'])
def like_point(point_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE points SET likes = likes + 1 WHERE id = ?", (point_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'liked'})

@app.route('/dislike_point/<int:point_id>', methods=['POST'])
def dislike_point(point_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT dislikes FROM points WHERE id = ?", (point_id,))
    dislikes = c.fetchone()[0] + 1
    if dislikes >= 10:
        c.execute("DELETE FROM points WHERE id = ?", (point_id,))
    else:
        c.execute("UPDATE points SET dislikes = ? WHERE id = ?", (dislikes, point_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'disliked'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
