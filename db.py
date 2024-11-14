import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG

# Databases connection for MySQL 
def get_db_connection():
    return mysql.connector.connect(
        host=DATABASE_CONFIG['HOST'],  
        user=DATABASE_CONFIG['USER'],  
        password=DATABASE_CONFIG['PASSWORD'],  
        database=DATABASE_CONFIG['DATABASE']  
    )

# Save guest information to database
def save_guest(first_name, last_name, email, phone):
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor()
        try:
            # Insert guest details into the Guest table
            cursor.execute(
                "INSERT INTO Guest (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, phone)
            )
            # Commit the transaction to the database
            connection.commit() 
            # Get the last inserted guest ID
            guest_id = cursor.lastrowid
            print(f"Guest saved with ID: {guest_id}")
            return guest_id
        except Error as e:
             # Handle any errors that occur
            print(f"Error saving guest: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

# Retrieve guest information by ID
def get_guest(guest_id):
    connection = get_db_connection()

    if connection:
        # Use dictionary cursor to fetch results as a dictionary
        cursor = connection.cursor(dictionary=True)
        try:
            # Fetch guest details from the Guest table using the guest ID
            cursor.execute("SELECT * FROM Guest WHERE id = %s", (guest_id,))
            # Get a result
            guest = cursor.fetchone()
            return guest
        except Error as e:
            print(f"Error retrieving guest: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

# Save reservation details to database
def save_reservation(guest_id, checkin, checkout, room_selection, vehicle_brand, vehicle_type, vehicle_quantity, total_price):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Insert new reservation into reservation table
        cursor.execute(
            "INSERT INTO Reservation (guest_id, payment_status) VALUES (%s, %s)",
            (guest_id, 'Pending')
        )

        connection.commit()
        # Get the ID of created reservation
        reservation_id = cursor.lastrowid

        # Insert into Room_reservation table for each room type and quantity
        for room_id, quantity in room_selection.items():
            # Add an entry for each room requested
            for _ in range(quantity):  
                cursor.execute(
                    '''
                    INSERT INTO Room_reservation (reservation_id, room_id, check_in_date, check_out_date, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ''',
                    (reservation_id, room_id, checkin, checkout, 'Reserved')
                )

        #Add vehicle information if provided
        if vehicle_brand and vehicle_type and vehicle_quantity > 0:
            # Insert vehicle entries for the reservation
            for _ in range(vehicle_quantity):
                cursor.execute(
                    '''
                    INSERT INTO Vehicles (type, brand, color, room_id)
                    VALUES (%s, %s, %s, %s)
                    ''',
                    (vehicle_type, vehicle_brand, 'Unknown', room_id)
                )

        connection.commit()
        # Return the reservation ID
        return reservation_id

    except Exception as e:
        print(f"Error creating reservation: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


# Retrieve reservation information by reservation id
def get_reservation(reservation_id):
    connection = get_db_connection()
    if connection:
        # Use dictionary cursor for results
        cursor = connection.cursor(dictionary=True)
        try:
            # Fetch reservation details from the Reservation table
            cursor.execute("SELECT * FROM Reservation WHERE id = %s", (reservation_id,))
            # Get result
            reservation = cursor.fetchone()
            # Return the reservation details
            return reservation
        except Error as e:
            print(f"Error retrieving reservation: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

