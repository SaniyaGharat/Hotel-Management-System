from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect Flask to MySQL Workbench
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",  # Add your MySQL password if set
    database="hotel_db"
)
cursor = db.cursor()

# 📌 Feature 1: User Registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    sql = "INSERT INTO User (name, email, password, role) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data['name'], data['email'], data['password'], "customer"))
    db.commit()
    return jsonify({"message": "User registered successfully!"})

# 📌 Feature 2: User Login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    sql = "SELECT * FROM User WHERE email = %s AND password = %s"
    cursor.execute(sql, (data['email'], data['password']))
    user = cursor.fetchone()
    if user:
        return jsonify({"message": "Login successful", "role": user[4]})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# 📌 Feature 3: Fetch Available Rooms
@app.route('/rooms', methods=['GET'])
def get_rooms():
    cursor.execute("SELECT * FROM Room WHERE status='Available'")
    rooms = cursor.fetchall()
    return jsonify(rooms)

# 📌 Feature 4: Book a Room
@app.route('/book', methods=['POST'])
def book_room():
    data = request.json
    sql = "INSERT INTO Booking (customer_id, room_id, checkin_date, checkout_date, total_cost) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (data['customer_id'], data['room_id'], data['checkin_date'], data['checkout_date'], data['total_cost']))
    cursor.execute("UPDATE Room SET status='Booked' WHERE room_id=%s", (data['room_id'],))
    db.commit()
    return jsonify({"message": "Room booked successfully!"})

# 📌 Feature 5: View Booking History
@app.route('/booking-history/<int:customer_id>', methods=['GET'])
def get_booking_history(customer_id):
    sql = "SELECT * FROM Booking WHERE customer_id = %s"
    cursor.execute(sql, (customer_id,))
    bookings = cursor.fetchall()
    return jsonify(bookings)

# 📌 Feature 6: Payment Processing
@app.route('/payment', methods=['POST'])
def make_payment():
    data = request.json
    sql = "INSERT INTO Payment (booking_id, amount, method, payment_date) VALUES (%s, %s, %s, NOW())"
    cursor.execute(sql, (data['booking_id'], data['amount'], data['method']))
    db.commit()
    return jsonify({"message": "Payment successful!"})

# 📌 Feature 7: Admin - Add Room
@app.route('/admin/add-room', methods=['POST'])
def add_room():
    data = request.json
    sql = "INSERT INTO Room (hotel_id, room_type, price, status) VALUES (%s, %s, %s, 'Available')"
    cursor.execute(sql, (data['hotel_id'], data['room_type'], data['price']))
    db.commit()
    return jsonify({"message": "Room added successfully!"})

# 📌 Feature 8: Admin - Remove Room
@app.route('/admin/delete-room/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    cursor.execute("DELETE FROM Room WHERE room_id=%s", (room_id,))
    db.commit()
    return jsonify({"message": "Room deleted successfully!"})

# 📌 Feature 9: Admin - View All Bookings
@app.route('/admin/bookings', methods=['GET'])
def view_all_bookings():
    cursor.execute("SELECT * FROM Booking")
    bookings = cursor.fetchall()
    return jsonify(bookings)

# 📌 Feature 10: Search & Filter Rooms
@app.route('/search', methods=['GET'])
def search_rooms():
    room_type = request.args.get('type')
    sql = "SELECT * FROM Room WHERE room_type=%s AND status='Available'"
    cursor.execute(sql, (room_type,))
    rooms = cursor.fetchall()
    return jsonify(rooms)

@app.route('/')
def home():
    return "Hotel Management System API is Running!"


if __name__ == '__main__':
    app.run(debug=True)
