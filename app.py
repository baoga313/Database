from flask import Flask, render_template, request, redirect, url_for, session
from db import save_guest, get_guest, save_reservation, get_reservation, get_db_connection
from datetime import datetime

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Define room prices 
ROOM_PRICES = {
    'king': 200,
    'queen': 150,
    'single': 100,
    'twin': 120
}

# Route for Home Page
@app.route('/')
def front_page():
    return render_template('home_page.html')


# Route for Guest Information Page
@app.route('/guest-form', methods=['GET', 'POST'])
def guest_form():

    # Handle submit fro guest info
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']

        # Save guest info and get guest_id
        guest_id = save_guest(first_name, last_name, email, phone)
        # Store guest_id in session
        session['guest_id'] = guest_id  

        return redirect(url_for('room_selection'))  
    return render_template('guest_form.html')



# Route for Room Selection Page
@app.route('/room-selection', methods=['GET', 'POST'])
def room_selection():
    # Retrieve guest id
    guest_id = session.get('guest_id')

    # Redirect to guest_form if guest_id is missing
    if not guest_id:
        return redirect(url_for('guest_form'))  

    # Handle room selection submission
    if request.method == 'POST':
        # Collect room quantities
        room_selection = {
            'king': int(request.form['king_room_quantity']),
            'queen': int(request.form['queen_room_quantity']),
            'single': int(request.form['single_room_quantity']),
            'twin': int(request.form['twin_room_quantity']),
        }
        # Store room selection in session
        session['room_selection'] = room_selection

        return redirect(url_for('extra_service'))

    return render_template('room_selection.html')



# Route for Extra Service Page
@app.route('/extra-service', methods=['GET', 'POST'])
def extra_service():
    # Retrieve guest id and room selection
    guest_id = session.get('guest_id')
    room_selection = session.get('room_selection')

    # Redirect to room selection if data is missing
    if not guest_id or not room_selection:
        return redirect(url_for('room_selection')) 

    # Handle extra services
    if request.method == 'POST':
        # Retrieve form data
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        vehicle_brand = request.form.get('vehicle_brand', '')
        vehicle_type = request.form.get('vehicle_type', '')
        vehicle_quantity = int(request.form.get('vehicle_quantity', 0))

        # Convert checkin and checkout to datetime
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')

        # Calculate the number of nights
        number_of_nights = (checkout_date - checkin_date).days

        # Calculate total price 
        total_price = sum(
            ROOM_PRICES[room_type] * quantity * number_of_nights 
            for room_type, quantity in room_selection.items()
        )

        # Save reservation 
        reservation_id = save_reservation(
            guest_id, checkin, checkout, room_selection, 
            vehicle_brand, vehicle_type, vehicle_quantity, total_price
        )

        # Store both guest_id and reservation_id in session
        session['checkin'] = checkin
        session['checkout'] = checkout
        session['reservation_id'] = reservation_id
        session['total_price'] = total_price
        session['vehicle_brand'] = vehicle_brand
        session['vehicle_type'] = vehicle_type
        session['vehicle_quantity'] = vehicle_quantity

        return redirect(url_for('confirmation_page'))

    return render_template('extra_service.html')

# Route for Confirmation Page
@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation_page():
    # Retrieve guest_id and reservation_id
    guest_id = session.get('guest_id')
    reservation_id = session.get('reservation_id')

     # Fetch guest and reservation details from the database
    guest = get_guest(guest_id)
    reservation = get_reservation(reservation_id)

     # Get room selection and other data 
    room_selection = session.get('room_selection')
    total_price = session.get('total_price')
    vehicle_brand = session.get('vehicle_brand')
    vehicle_type = session.get('vehicle_type')
    vehicle_quantity = session.get('vehicle_quantity')
    checkin = session.get('checkin') 
    checkout = session.get('checkout')  

    if request.method == 'POST':
        return redirect(url_for('payment_page'))  

    return render_template('confirmation_page.html', 
                           guest=guest, 
                           reservation=reservation, 
                           room_selection=room_selection,
                           total_price=total_price,
                           vehicle_brand=vehicle_brand,
                           vehicle_type=vehicle_type,
                           vehicle_quantity=vehicle_quantity,
                           checkin=checkin, checkout=checkout)  


# Route for Payment Page
@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    return render_template('payment_page.html')


if __name__ == '__main__':
    app.run(debug=True)