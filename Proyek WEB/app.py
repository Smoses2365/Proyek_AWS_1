from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config["MYSQL_USER"] = "admin"
app.config["MYSQL_PASSWORD"] = "klaudaws6785"
app.config["MYSQL_HOST"] = "database-1.cc9qg6abmvfv.us-east-1.rds.amazonaws.com"
app.config["MYSQL_DB"] = "car_rental_dbs"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.secret_key = "secret"

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/sewa")
def sewa():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cars")
    cars = cur.fetchall()
    cur.close()
    return render_template("sewa.html", cars=cars)

@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, username, email, password, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["email"] = user["email"]

            flash("Login berhasil!", "success")
            return redirect(url_for("home"))

        flash("Username atau password salah", "danger")
    
    return render_template("sign_in.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        phone = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Email sudah terdaftar, gunakan email lain!", "warning")
            return redirect(url_for("sign_up"))

        cur.execute("""
            INSERT INTO users (username, password, email, phone_number, role) 
            VALUES (%s, %s, %s, %s, 'member')
        """, (username, hashed_password, email, phone))
        
        mysql.connection.commit()
        cur.close()

        flash("Pendaftaran berhasil! Silakan Sign In.", "success")
        return redirect(url_for("sign_in"))

    return render_template("sign_up.html")

@app.route("/rent_car", methods=["POST"])
def rent_car():
    if not session.get('user_id'):
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('sign_in'))

    user_id = session.get('user_id')
    car_id = request.form.get('car_id')  # Ambil car_id dari form
    rental_date = request.form.get('rental_date')
    return_date = request.form.get('return_date')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT price_per_day FROM cars WHERE car_id = %s", (car_id,))
    car = cursor.fetchone()
    if not car:
        flash("Mobil tidak ditemukan.", "danger")
        return redirect(url_for('sewa'))

    rental_days = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(rental_date, "%Y-%m-%d")).days
    total_price = rental_days * car["price_per_day"]

    cursor.execute("""
        INSERT INTO rentals (user_id, car_id, rental_date, return_date, total_price, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
    """, (user_id, car_id, rental_date, return_date, total_price))
    mysql.connection.commit()
    cursor.close()

    flash("Penyewaan berhasil! Menunggu persetujuan admin.", "success")
    return redirect(url_for("home"))

@app.route("/rental_history")
def rental_history():
    if not session.get("user_id"):
        return redirect(url_for("sign_in"))

    cur = mysql.connection.cursor()

    if session.get("role") == "admin":
        # Admin melihat semua rental history dengan username
        cur.execute("""
            SELECT users.username, rentals.rental_date, rentals.return_date, 
                   rentals.total_price, rentals.status, cars.name AS car_name 
            FROM rentals 
            JOIN cars ON rentals.car_id = cars.car_id
            JOIN users ON rentals.user_id = users.user_id
        """)
    else:
        # User hanya melihat rental history miliknya
        cur.execute("""
            SELECT rentals.rental_date, rentals.return_date, 
                   rentals.total_price, rentals.status, cars.name AS car_name 
            FROM rentals 
            JOIN cars ON rentals.car_id = cars.car_id
            WHERE rentals.user_id = %s
        """, (session["user_id"],))

    history = cur.fetchall()
    cur.close()
    
    return render_template("rental_history.html", history=history, role=session["role"])


@app.route("/rental_approval", methods=["GET", "POST"])
def rent_approval():
    if session.get("role") != "admin":
        return redirect(url_for("home"))

    cur = mysql.connection.cursor()

    if request.method == "POST":
        rental_id = request.form.get("rental_id")
        action = request.form.get("action")

        if action == "approve":
            cur.execute("UPDATE rentals SET status = 'approved' WHERE rental_id = %s", (rental_id,))
            flash("Penyewaan disetujui!", "success")
        elif action == "reject":
            cur.execute("UPDATE rentals SET status = 'rejected' WHERE rental_id = %s", (rental_id,))
            flash("Penyewaan ditolak!", "danger")

        mysql.connection.commit()

    # Ambil semua rental yang masih pending
    cur.execute("""
        SELECT rentals.rental_id, users.username, cars.name AS car_name, rentals.rental_date, rentals.return_date, 
               rentals.total_price, rentals.status 
        FROM rentals 
        JOIN users ON rentals.user_id = users.user_id
        JOIN cars ON rentals.car_id = cars.car_id
        WHERE rentals.status = 'pending'
    """)
    pending_rentals = cur.fetchall()
    cur.close()

    return render_template("rent_approval.html", pending_rentals=pending_rentals)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
