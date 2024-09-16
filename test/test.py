from flask import Flask, request, render_template, send_file, make_response
import mysql.connector
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# Simplified database connection function
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",     
            user="root", 
            password="password", 
            database="user_rfid"  
        )
        if connection.is_connected():
            print("Connected to the database successfully.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Check if the user already exists in the database
def user_exists(name, surname, role, cursor):
    query = "SELECT COUNT(*) FROM user_QRinfo WHERE name = %s AND surname = %s AND role = %s"
    cursor.execute(query, (name, surname, role))
    count = cursor.fetchone()[0]
    return count > 0

# Generate a unique QR code based on user details
def generate_qr_code(name, surname, role):
    unique_string = f"{name}{surname}{role}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Save QR code image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Add user and QR code to the database
def add_user_to_db(name, surname, role, qr_code_data):
    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        if user_exists(name, surname, role, cursor):
            print(f"User {name} {surname} with role {role} already exists.")
            return "User already exists."

        # SQL query to insert user details and QR code
        query = "INSERT INTO user_QRinfo (name, surname, role, qr_code) VALUES (%s, %s, %s, %s)"
        values = (name, surname, role, qr_code_data)
        
        cursor.execute(query, values)
        connection.commit()
        print(f"User {name} {surname} with role {role} added successfully. QR code generated.")
        return "User added successfully."
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return f"Error: {err}"
    
    finally:
        cursor.close()
        close_db(connection)

# Close the connection
def close_db(connection):
    if connection.is_connected():
        connection.close()
        print("Database connection closed.")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        role = request.form['role']
        
        # Generate QR code for the user
        qr_code_buffer = generate_qr_code(name, surname, role)
        
        # Add user to the database and check for success
        result_message = add_user_to_db(name, surname, role, qr_code_buffer.getvalue())
        
        # Convert the QR code image to base64 string for display in HTML
        qr_code_buffer.seek(0)
        qr_code_base64 = base64.b64encode(qr_code_buffer.getvalue()).decode('utf-8')
        
        return render_template('signup.html', result_message=result_message, qr_code_data=qr_code_base64)
    
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True)
