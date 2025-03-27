from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database Connection Configuration
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'hotel_management')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None

# Test Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hotel Management API is running"}), 200

# Room Management Routes
@app.route('/rooms', methods=['GET'])
def get_rooms():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms")
    rooms = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(rooms)

@app.route('/rooms/available', methods=['GET'])
def get_available_rooms():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms WHERE status = 'Available'")
    rooms = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(rooms)

# Reservation Route with Payment Processing
@app.route('/reserve', methods=['POST'])
def create_reservation():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Insert Guest
        cursor.execute("""
            INSERT INTO Guests (first_name, last_name, email, phone_number) 
            VALUES (%s, %s, %s, %s)
        """, (
            data['first_name'], 
            data['last_name'], 
            data['email'], 
            data['phone']
        ))
        guest_id = cursor.lastrowid
        
        # Calculate total cost
        cursor.execute("SELECT rate_per_night FROM Rooms WHERE room_id = %s", (data['room_id'],))
        room_rate = cursor.fetchone()[0]
        
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d')
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d')
        nights = (check_out - check_in).days
        total_cost = room_rate * nights

        # Create Reservation
        cursor.execute("""
            INSERT INTO Reservations 
            (guest_id, room_id, check_in_date, check_out_date, total_cost) 
            VALUES (%s, %s, %s, %s, %s)
        """, (guest_id, data['room_id'], data['check_in'], data['check_out'], total_cost))
        reservation_id = cursor.lastrowid

        # Insert Payment (Ensure lowercase table name `payments`)
        cursor.execute("""
            INSERT INTO payments (reservation_id, amount, payment_status)
            VALUES (%s, %s, %s)
        """, (reservation_id, total_cost, 'Pending'))  # Default status is "Pending"

        # Update Room Status
        cursor.execute("UPDATE Rooms SET status = 'Occupied' WHERE room_id = %s", (data['room_id'],))

        # Commit all changes
        conn.commit()

        return jsonify({
            "message": "Reservation successful",
            "reservation_id": reservation_id,
            "total_cost": total_cost,
            "payment_status": "Pending"
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
