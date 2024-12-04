import mysql.connector 

# Configure the MySQL database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",               # Update with your MySQL host
        user="root",      # Your MySQL username
        password="password",  # Your MySQL password
        database="hotel_reservation"    # Your database name
    )