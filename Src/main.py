from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
from werkzeug.utils import secure_filename
import sys, os
sys.path.append(os.path.relpath("./db"))
import db
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

login_manager = LoginManager()
login_manager.init_app(app)

# Example User class
class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(userId):
    # Example function to load a user from a database
    # Replace with your actual user loading logic
    user = db.getUserById(userId)
    if user:
        return User(userId, user['username'], user.get("is_admin", False))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('store'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.getUserByUsername(username, password)
        if user and db.checkLogin(username, password):  # You should use hashed passwords
            userObj = User(user['id'], username)
            userObj.username = user['username']
            login_user(userObj)
            return redirect(url_for('store'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('store'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # You may want to add more validation here
        db.createUser(username, email, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/store')
def store():
    # Get the error message, if any, from the query parameters
    error = request.args.get('error')

    # Add logic to retrieve and display bikes from the database
    bikes = db.getListBikes()
    return render_template('store.html', bikes=bikes, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<string:bike_id>', methods=['POST'])
def add_to_cart(bike_id):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])
    
    # Get the available count of the bike from the database
    available_count = db.getAvailableBikeCount(bike_id)
    counter = 0
    for x in cart:
        if x.get('bike_id') == bike_id:
            counter = counter + 1
    if counter == available_count:
        error = 'Exceeded available bike count'
        return redirect(url_for('store', error=error))
    else:
        cart.append({'bike_id': bike_id, 'hours': 1})
        # Store the updated cart back into the session
        session['cart'] = cart
        
        # Redirect the user back to the store page
        return redirect(url_for('store', error=None))


@app.route('/view_cart')
def view_cart():
    # Retrieve the current cart from the session
    cart = session.get('cart', [])
    
    # Initialize a list to store cart items with bike details
    cart_items = []
    total_price = 0
    
    # Loop through items in the cart
    for item in cart:
        # Retrieve bike information from the database based on bike_id
        bike = db.getBikeById(item['bike_id'])
        
        # Check if the bike exists
        if bike:
            # Calculate the total price for the item
            item_total_price = bike['price_per_hour'] * item['hours']
            
            # Add the item with bike details to the cart_items list
            cart_items.append({
                'bike': bike,
                'hours': item['hours'],
                'total_price': item_total_price
            })
            
            # Update the total price
            total_price += item_total_price
    
    # Render the cart template with cart items and total price
    return render_template('cart.html', cart=cart_items, total_price=total_price)

@app.route('/update_cart/<int:index>', methods=['POST'])
def update_cart(index):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])
    
    # Retrieve the updated hours from the form
    updated_hours = int(request.form['hours'])
    
    # Fetch the price per hour of the bike from the database
    bike_id = cart[index]['bike_id']
    bike = db.getBikeById(bike_id)
    price_per_hour = bike['price_per_hour']
    
    # Update the hours for the specified item in the cart
    cart[index]['hours'] = updated_hours
    
    # Update the total price for the item
    cart[index]['total_price'] = price_per_hour * updated_hours
    
    # Store the updated cart back into the session
    session['cart'] = cart
    
    # Redirect the user back to the view_cart page
    return redirect(url_for('view_cart'))

@app.route('/delete_bike_cart/<int:index>', methods=['POST'])
def delete_bike_cart(index):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])
    
    # Remove the bike at the specified index from the cart
    del cart[index]
    
    # Store the updated cart back into the session
    session['cart'] = cart
    
    # Redirect the user back to the view_cart page
    return redirect(url_for('view_cart'))

def creditCardChecker(cardNumber, cvv, expiryDate):
    # For demo purposes, we'll assume any card number with 16 digits is valid
    # You can implement more sophisticated validation logic if needed
    if len(cardNumber) != 16:
        return False

    # For demo purposes, we'll assume CVV must be 3 digits
    if len(cvv) != 3 or not cvv.isdigit():
        return False

    # Check if expiry date is in the format MM/YY and is not expired
    try:
        expiryMonth, expiryYear = map(int, expiryDate.split('/'))
        expiryDate = datetime(year=2000 + expiryYear, month=expiryMonth, day=1)
        currentDate = datetime.now()
        if expiryDate < currentDate:
            return False
    except:
        return False

    return True

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    cart_items = []
    total_price = 0
    error = None
    # Loop through items in the cart
    for item in cart:
        # Retrieve bike information from the database based on bike_id
        bike = db.getBikeById(item['bike_id'])
        
        # Check if the bike exists
        if bike:
            # Calculate the total price for the item
            item_total_price = bike['price_per_hour'] * item['hours']
            
            # Add the item with bike details to the cart_items list
            cart_items.append({
                'bike': bike,
                'hours': item['hours'],
                'total_price': item_total_price
            })
            
            # Update the total price
            total_price += item_total_price
    if request.method == 'POST':
         # Retrieve credit card number from the form
        creditCardNumber = request.form.get('card_number')
        cvv = request.form.get('cvv')
        expiryDate = request.form.get('expiry_date')

        # Validate the credit card number
        if creditCardChecker(creditCardNumber, cvv, expiryDate):
            # Payment successful, clear the cart or mark items as purchased
            session.pop('cart', None)  # Clear the cart after successful payment

            # Redirect to a thank you page or display a success message
            return redirect(url_for('thank_you'))
        else:
            # Payment failed due to invalid credit card
            error = "Invalid credit card number. Please try again."
            return render_template('checkout.html', error=error, cart=cart_items, total_price=total_price)
    # Initialize a list to store cart items with bike details
    # Retrieve the current cart from the session
    # Render the checkout template with the cart and total price
    return render_template('checkout.html',error=error, cart=cart_items, total_price=total_price)


@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')



@app.route('/admin', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in admins can access this page
def admin():
    if not current_user.is_admin:
        return "Unauthorized - Only admin users can access this page.", 401  # Return unauthorized status code
    if request.method == 'POST':
        # Handle form submission to add a new bike
        name = request.form['name']
        type = request.form['type']
        price_per_hour = float(request.form['price_per_hour'])
        availability = int(request.form['availability'])
        
        # Handle file upload
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Add the bike to the database
        db.addBike(name, type, price_per_hour, availability, filename)
        
        return redirect(url_for('admin'))  # Redirect to the admin page after adding the bike
    bikes = db.getListBikes()
    print(bikes)
    
    return render_template('admin.html', bikes=bikes)

# Define a route to remove a bike
@app.route('/remove_bike/<int:bike_id>', methods=['POST'])
@login_required
def remove_bike(bike_id):
    # Remove the bike from the database
    db.removeBike(bike_id)
    return redirect(url_for('admin'))  # Redirect to the admin page after removing the bike

if __name__ == '__main__':
    db.createDatabase()
    app.config['UPLOAD_FOLDER'] = 'src/static/uploads'
    app.run(debug=True)