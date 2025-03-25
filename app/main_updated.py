import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import sqlite3

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
            dislikes INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            point_id INTEGER,
            user_id INTEGER,
            vote_type TEXT CHECK(vote_type IN ('like', 'dislike')),
            UNIQUE(point_id, user_id)
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
    image_file = request.files.get('image')
    image_path = ''
    if image_file:
        filename = secure_filename(image_file.filename)
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(saved_path)
        image_path = f'/static/uploads/{filename}'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO points (lat, lon, comment, image) VALUES (?, ?, ?, ?)",
              (lat, lon, comment, image_path))
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

@app.route('/like_point/<int:point_id>', methods=['POST'])
def like_point(point_id):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM votes WHERE point_id = ? AND user_id = ?", (point_id, user_id))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "already voted"}), 403

    c.execute("UPDATE points SET likes = likes + 1 WHERE id = ?", (point_id,))
    c.execute("INSERT INTO votes (point_id, user_id, vote_type) VALUES (?, ?, ?)",
              (point_id, user_id, 'like'))
    conn.commit()
    conn.close()
    return jsonify({'status': 'liked'})

@app.route('/dislike_point/<int:point_id>', methods=['POST'])
def dislike_point(point_id):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM votes WHERE point_id = ? AND user_id = ?", (point_id, user_id))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "already voted"}), 403

    c.execute("SELECT dislikes FROM points WHERE id = ?", (point_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "point not found"}), 404

    dislikes = row[0] + 1
    if dislikes >= 10:
        c.execute("DELETE FROM points WHERE id = ?", (point_id,))
    else:
        c.execute("UPDATE points SET dislikes = ? WHERE id = ?", (dislikes, point_id))

    c.execute("INSERT INTO votes (point_id, user_id, vote_type) VALUES (?, ?, ?)",
              (point_id, user_id, 'dislike'))
    conn.commit()
    conn.close()
    return jsonify({'status': 'disliked'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))