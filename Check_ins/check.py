from flask import Flask, render_template, request, send_file, redirect, url_for
import mysql.connector
import qrcode
from io import BytesIO

app = Flask(__name__)

# Database connection
def connect_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="user_rfid"
    )
    return connection

# QR Code generation
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    
    # Save image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Add user and generate QR code
@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    surname = request.form['surname']
    role = request.form['role']
    
    user_data = f"{name}{surname}{role}"
    
    # Generate QR code
    qr_code_img = generate_qr_code(user_data)
    
    # Insert user info into database with QR code
    connection = connect_db()
    cursor = connection.cursor()
    query = "INSERT INTO user_info (name, surname, role, qr_code) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, surname, role, qr_code_img.read()))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('list_users'))

# List all users and display QR codes
@app.route('/list_users')
def list_users():
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT id, name, surname, role FROM user_info"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('list_users.html', users=users)

# Download QR code for a specific user
@app.route('/get_qr_code/<int:user_id>')
def get_qr_code(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT qr_code FROM user_info WHERE id = %s"
    cursor.execute(query, (user_id,))
    qr_code = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    
    return send_file(BytesIO(qr_code), mimetype='image/png')

# Check user presence by scanning the QR code
@app.route('/scan', methods=['POST'])
def scan_qr():
    scanned_data = request.form['scanned_data']  # This would be the QR code data from scanner
    
    # Find the user in the database based on scanned data
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT id FROM user_info WHERE CONCAT(name, surname, role) = %s"
    cursor.execute(query, (scanned_data,))
    user_id = cursor.fetchone()
    
    if user_id:
        user_id = user_id[0]
        
        # Check the user's current status
        query = "SELECT event_type FROM user_presence WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query, (user_id,))
        last_event = cursor.fetchone()
        
        if last_event and last_event[0] == 'check-in':
            # If last event was check-in, now log check-out
            query = "INSERT INTO user_presence (user_id, event_type) VALUES (%s, 'check-out')"
            cursor.execute(query, (user_id,))
        else:
            # If last event was check-out or no event, log check-in
            query = "INSERT INTO user_presence (user_id, event_type) VALUES (%s, 'check-in')"
            cursor.execute(query, (user_id,))
        
        connection.commit()
        message = "User status updated successfully."
    else:
        message = "User not found."
    
    cursor.close()
    connection.close()
    
    return message

if __name__ == "__main__":
    app.run(debug=True)
