import mysql.connector
import hashlib

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

# Generate a unique RFID code based on user details
def generate_rfid(name, surname, role):
    unique_string = f"{name}{surname}{role}"
    rfid_code = hashlib.sha256(unique_string.encode()).hexdigest()[:10]  # Take first 10 characters of the hash
    return rfid_code

# Add user and RFID code to the database
def add_user_to_db(name, surname, role):
    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        # Generate RFID code for the user
        rfid_code = generate_rfid(name, surname, role)
        
        # SQL query to insert user details and RFID code
        query = "INSERT INTO user_info (name, surname, role, rfid_code) VALUES (%s, %s, %s, %s)"
        values = (name, surname, role, rfid_code)
        
        cursor.execute(query, values)
        connection.commit()
        print(f"User {name} {surname} with role {role} added successfully. RFID: {rfid_code}")
    
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
