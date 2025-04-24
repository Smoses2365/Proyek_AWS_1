import mysql.connector
from mysql.connector import errorcode
from flask import Flask, request, jsonify

# ----------------------------
# Konfigurasi koneksi MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',       # ganti sesuai user MySQL-mu
    'password': 'password',  # ganti sesuai password
    'database': 'todo_event_db'
}

# Buat koneksi ke MySQL
def init_db():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        # Buat database jika belum ada
        cursor.execute("CREATE DATABASE IF NOT EXISTS {} CHARACTER SET utf8mb4".format(db_config['database']))
        conn.database = db_config['database']

        # Buat tabel todos
        create_todos = (
            "CREATE TABLE IF NOT EXISTS todos ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  title VARCHAR(255) NOT NULL,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB"
        )
        cursor.execute(create_todos)

        # Buat tabel events
        create_events = (
            "CREATE TABLE IF NOT EXISTS events ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  name VARCHAR(255) NOT NULL,"
            "  date DATE NOT NULL,"
            "  category ENUM('absolutely important','important','moderate') NOT NULL,
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB"
        )
        cursor.execute(create_events)

        cursor.close()
        conn.close()
        print("Database dan tabel berhasil diinisialisasi.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Username atau password MySQL salah.")
        else:
            print(err)

# Panggil init_db saat script dijalankan
init_db()

# ----------------------------
# Aplikasi Flask
app = Flask(name)

# Helper untuk membuat koneksi baru
def get_connection():
    return mysql.connector.connect(**db_config)

# Endpoint GET /todos
@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, created_at FROM todos ORDER BY created_at ASC")
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(todos)

# Endpoint POST /todos
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    title = data.get('title')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("INSERT INTO todos (title) VALUES (%s)", (title,))
    conn.commit()
    todo_id = cursor.lastrowid
    cursor.execute("SELECT id, title, created_at FROM todos WHERE id = %s", (todo_id,))
    new_todo = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(new_todo), 201

# Endpoint GET /events/notifications
@app.route('/events/notifications', methods=['GET'])
def get_events():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, DATE_FORMAT(date, '%Y-%m-%d') AS date, category "
        "FROM events ORDER BY date ASC"
    )
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(events)

# Endpoint POST /events
@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()
    name = data.get('name')
    date = data.get('date')
    category = data.get('category')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO events (name, date, category) VALUES (%s, %s, %s)",
        (name, date, category)
    )
    conn.commit()
    event_id = cursor.lastrowid
    cursor.execute(
        "SELECT id, name, DATE_FORMAT(date, '%Y-%m-%d') AS date, category FROM events WHERE id = %s",
        (event_id,)
    )
    new_event = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(new_event), 201
if "name" == 'main':
    app.run(debug=True, port=3000)