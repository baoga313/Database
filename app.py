from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import get_user_by_email, create_user, get_reservations, update_reservation_status, create_reservation, add_room_to_reservation, add_vehicle_to_reservation, calculate_total_price, create_payment, VALID_STATUSES
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    #Get user details from database
    user = get_user_by_email(email)
    if user and check_password_hash(user['Password'], password):  
        # Store GuestID in session
        session['user_id'] = user['GuestID']  
        session['user_email'] = user['Email']
        return redirect(url_for('home'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('signup'))

    try:
        create_user(first_name, last_name, email, phone_number, password)
        flash("Account created successfully")
        return redirect(url_for('login'))
    except Exception as e:
        flash("Error: Email already exists")
        return redirect(url_for('signup'))
    
@app.route('/logout')
def logout():
    # Clear the session and redirect to the login page
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get reservations for the logged-in user
    reservations = get_reservations(session['user_id']) 
    return render_template('home.html', reservations=reservations)

@app.route('/update_status/<int:reservation_id>/<status>', methods=['GET', 'POST'])
def update_status(reservation_id, status):
    # Update the reservation status
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if status not in VALID_STATUSES:
        return redirect(url_for('home'))

    try:
        update_reservation_status(reservation_id, status)
        
    except Exception as e:
        flash(f"Error updating reservation status: {e}", "error")

    # Fetch the updated list of reservations
    reservations = get_reservations(session['user_id'])

    return render_template('home.html', reservations=reservations)

@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve selected quantities of rooms
        rooms = [
            {'RoomType': 'King Room', 'Quantity': int(request.form.get('king_quantity', 0))},
            {'RoomType': 'Queen Room', 'Quantity': int(request.form.get('queen_quantity', 0))},
            {'RoomType': 'Twin Room', 'Quantity': int(request.form.get('twin_quantity', 0))},
            {'RoomType': 'Single Room', 'Quantity': int(request.form.get('single_quantity', 0))}
        ]

        # Check if at least one room is selected
        if all(room['Quantity'] == 0 for room in rooms):
            flash("Please select at least one room.", "error")
            return redirect(url_for('make_reservation'))

        # Store room reservation data for the next page
        session['reservation_data'] = rooms

        return redirect(url_for('extra_service'))

    return render_template('make_reservation.html')

@app.route('/extra_service', methods=['GET', 'POST'])
def extra_service():
    if request.method == 'POST':
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        brand = request.form['brand']
        vehicle_type = request.form['type']
        quantity = int(request.form['quantity'])

        # Save vehicle data to session 
        vehicle_data = {'Brand': brand, 'Type': vehicle_type, 'Quantity': quantity}
        session['vehicle_data'] = [vehicle_data]  # Store in session for confirmation page

        session['check_in_date'] = check_in_date
        session['check_out_date'] = check_out_date

        return redirect(url_for('confirmation'))
    return render_template('extra_service.html')

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if 'user_id' not in session or 'reservation_data' not in session:
        return redirect(url_for('make_reservation'))

    user_email = session['user_email']
    user = get_user_by_email(user_email)

    #Load reservation data from session
    rooms = session['reservation_data']
    vehicles = session.get('vehicle_data', [])  
    check_in_date = session['check_in_date']
    check_out_date = session['check_out_date']

    if request.method == 'POST':
        reservation_id = create_reservation(session['user_id'])

        # Add rooms
        for room in rooms:
            if room['Quantity'] > 0:
                add_room_to_reservation(reservation_id, room['RoomType'], room['Quantity'], check_in_date, check_out_date)

        # Add vehicles
        for vehicle in vehicles:
            add_vehicle_to_reservation(reservation_id, vehicle['Brand'], vehicle['Type'], vehicle['Quantity'])

        # Save reservation_id in session to access it in the payment page
        session['reservation_id'] = reservation_id

        return redirect(url_for('payment'))

    return render_template('confirmation.html', user=user, rooms=rooms, vehicles=vehicles, check_in_date=check_in_date, check_out_date=check_out_date)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session or 'reservation_id' not in session:
        return redirect(url_for('make_reservation'))  # Redirect if no reservation found


    reservation_id = session['reservation_id']
    total_price = calculate_total_price(reservation_id)

    if request.method == 'POST':
        payment_method = request.form['payment_method']
        payment_status = 'Completed'
        payment_date = datetime.today().strftime('%Y-%m-%d')

        # Store the payment information in the database
        create_payment(reservation_id, payment_method, payment_status, payment_date)

        # Update the reservation status
        update_reservation_status(reservation_id, 'Completed')

        return redirect(url_for('home'))  # Redirect to the homepage or confirmation page

    return render_template('payment.html', total_price=total_price)

@app.route('/cancel_payment')
def cancel_payment():
    # Simply redirect to the home page without making any changes to the database
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)