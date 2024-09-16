import mysql.connector
import hashlib
import qrcode
from io import BytesIO

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
    qr_code_data = buffer.getvalue()
    return qr_code_data

# Add user and QR code to the database
def add_user_to_db(name, surname, role):
    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        # Generate QR code for the user
        qr_code_data = generate_qr_code(name, surname, role)
        
        # SQL query to insert user details and QR code
        query = "INSERT INTO user_QRinfo (name, surname, role, qr_code) VALUES (%s, %s, %s, %s)"
        values = (name, surname, role, qr_code_data)
        
        cursor.execute(query, values)
        connection.commit()
        print(f"User {name} {surname} with role {role} added successfully. QR code generated.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        cursor.close()
        close_db(connection)

# Close the connection
def close_db(connection):
    if connection.is_connected():
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    # Input user details
    name = input("Enter user's name: ")
    surname = input("Enter user's surname: ")
    role = input("Enter user's role (student, staff, grizzly, intern): ")
    
    add_user_to_db(name, surname, role)
