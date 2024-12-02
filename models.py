from db import get_db
from datetime import datetime

# Fetch user from the database based on email
def get_user_by_email(email):
    db = get_db()  
    try:
        query = "SELECT * FROM Guest WHERE Email = %s"
        cursor = db.cursor(dictionary=True)  
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        db.close()

# Create a new user in the database
def create_user(first_name, last_name, email, phone_number, password):
    db = get_db()
    try:
        query = """
            INSERT INTO Guest (FirstName, LastName, Email, PhoneNumber, Password)
            VALUES (%s, %s, %s, %s, %s)
        """  
        cursor = db.cursor()
        cursor.execute(query, (first_name, last_name, email, phone_number, password))
        db.commit()
    finally:
        cursor.close()
        db.close()

# Fetch reservations for a specific user
def get_reservations(user_id):
    db = get_db()
    try:
        query = """
            SELECT Reservation.ReservationID, 
                   MIN(RoomReservation.CheckInDate) AS CheckInDate, 
                   MAX(RoomReservation.CheckOutDate) AS CheckOutDate, 
                   Reservation.Status AS ReservationStatus
            FROM Reservation
            JOIN RoomReservation ON Reservation.ReservationID = RoomReservation.ReservationID
            WHERE Reservation.GuestID = %s
            GROUP BY Reservation.ReservationID, Reservation.Status
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        reservations = cursor.fetchall()
        return reservations
    finally:
        cursor.close()
        db.close()

# Unified valid statuses
VALID_STATUSES = ['Pending', 'Reserved', 'Checked In', 'Cancelled']

# Update reservation status
def update_reservation_status(reservation_id, status):
    if status not in VALID_STATUSES:
        raise ValueError("Invalid status value")

    db = get_db()  
    try:
        # Update RoomReservation Status
        room_reservation_query = """
            UPDATE RoomReservation 
            SET Status = %s 
            WHERE ReservationID = %s
        """
        cursor = db.cursor()
        cursor.execute(room_reservation_query, (status, reservation_id))
        db.commit()

        # Update Reservation Status
        reservation_query = """
            UPDATE Reservation 
            SET Status = %s 
            WHERE ReservationID = %s
        """
        cursor.execute(reservation_query, (status, reservation_id))
        db.commit()

        # Update Payment Status 
        if status == 'Cancelled':
            payment_status = 'Cancelled'
        elif status in ['Reserved', 'Checked In']:
            payment_status = 'Completed'
        else:
            payment_status = 'Pending'

        payment_query = """
            UPDATE Payment 
            SET Status = %s 
            WHERE ReservationID = %s
        """
        cursor.execute(payment_query, (payment_status, reservation_id))
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error updating status: {e}")
        raise e
    finally:
        cursor.close()
        db.close()

# Create a new reservation
def create_reservation(user_id):
    db = get_db()
    try:
        query = "INSERT INTO Reservation (GuestID, Status) VALUES (%s, 'Pending')"
        cursor = db.cursor()
        cursor.execute(query, (user_id,))
        db.commit()
        return cursor.lastrowid  # Return the ReservationID
    finally:
        cursor.close()
        db.close()

# Add room details to a reservation
# Add rooms to a reservation
def add_room_to_reservation(reservation_id, room_type, quantity, check_in_date, check_out_date):
    db = get_db()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT RoomID FROM Room WHERE RoomType = %s", (room_type,))
        room = cursor.fetchone()
        if room:
            query = """
                INSERT INTO RoomReservation (ReservationID, RoomID, CheckInDate, CheckOutDate, Status, Quantity)
                VALUES (%s, %s, %s, %s, 'Pending', %s)
            """
            cursor.execute(query, (reservation_id, room['RoomID'], check_in_date, check_out_date, quantity))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error adding room to reservation: {e}")

# Add vehicles to a reservation
def add_vehicle_to_reservation(reservation_id, brand, vehicle_type, quantity):
    db = get_db()
    try:
        cursor = db.cursor(dictionary=True)
        
        # Fetch VehicleID
        cursor.execute("SELECT VehicleID FROM Vehicle WHERE Brand = %s AND Type = %s", (brand, vehicle_type))
        vehicle = cursor.fetchone()

        if vehicle:
            query = """
                INSERT INTO VehicleReservation (ReservationID, VehicleID, Quantity)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (reservation_id, vehicle['VehicleID'], quantity))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error adding vehicle to reservation: {e}")
    finally:
        cursor.close()
        db.close()

# Define valid payment statuses
VALID_PAYMENT_STATUS = ['Pending', 'Completed', 'Cancelled']

# Function to create a payment entry
def create_payment(reservation_id, payment_method, payment_status, payment_date, total_price):
    db = get_db()
    cursor = db.cursor()

    # Ensure the payment status is valid
    if payment_status not in VALID_PAYMENT_STATUS:
        raise ValueError(f"Invalid payment status: {payment_status}")
    
    try:
        query = """
            INSERT INTO Payment (ReservationID, PaymentMethod, Status, PaymentDate, TotalPrice)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor = db.cursor()
        cursor.execute(query, (reservation_id, payment_method, payment_status, payment_date, total_price))

        # If payment is completed, update the reservation status to Reserved
        if payment_status == 'Completed':
            reservation_query = """
                UPDATE Reservation 
                SET Status = 'Reserved'
                WHERE ReservationID = %s
            """
            cursor.execute(reservation_query, (reservation_id,))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()

# Function to calculate the total price for a reservation
def calculate_total_price(reservation_id):
    db = get_db()
    total_price = 0
    try:
        # Get room reservations and calculate the total price
        query = """
            SELECT r.PricePerNight, rr.Quantity, rr.CheckInDate, rr.CheckOutDate
            FROM RoomReservation rr
            JOIN Room r ON rr.RoomID = r.RoomID
            WHERE rr.ReservationID = %s
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (reservation_id,))
        room_reservations = cursor.fetchall()

        for room in room_reservations:
            room_price = room['PricePerNight']
            quantity = room['Quantity']
            check_in_date = room['CheckInDate']  
            check_out_date = room['CheckOutDate']  
            stay_duration = (check_out_date - check_in_date).days
            if stay_duration > 0:
                total_price += room_price * quantity * stay_duration

    finally:
        cursor.close()
        db.close()
    
    return total_price