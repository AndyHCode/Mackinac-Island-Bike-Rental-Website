from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
from werkzeug.utils import secure_filename
import sys, os
sys.path.append(os.path.relpath("./db"))
import db

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
    # Add logic to retrieve and display bikes from the database
    bikes = db.getListBikes()
    return render_template('store.html', bikes=bikes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_to_cart/<int:bike_id>/<int:quantity>', methods=['POST'])
def add_to_cart(bike_id, quantity):
    # Retrieve the current cart from the session
    cart = session.get('cart', {})
    
    # Update the cart with the new item
    if bike_id in cart:
        cart[bike_id] += quantity  # If the bike already exists in the cart, update its quantity
    else:
        cart[bike_id] = quantity  # If the bike is not in the cart, add it with the specified quantity
    
    # Store the updated cart back into the session
    session['cart'] = cart
    
    # Redirect the user back to the store page
    return redirect(url_for('store'))

@app.route('/view_cart')
@login_required
def view_cart():
    # Retrieve the user's cart from the session
    cart = session.get('cart', {})
    
    # Fetch details of bikes in the cart from the database
    cart_details = []
    total_price = 0
    
    for bike_id, quantity in cart.items():
        bike = db.getBikeById(bike_id)
        if bike:
            cart_details.append({
                'bike': bike,
                'quantity': quantity
            })
            total_price += bike['price_per_hour'] * quantity
    
    return render_template('cart.html', cart=cart_details, total_price=total_price)

@app.route('/update_cart/<int:item_id>/<int:quantity>')
@login_required
def update_cart(item_id, quantity):
    # Logic to update the quantity of an item in the user's cart
    # Update the session or database accordingly
    pass

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    # Logic to remove an item from the user's cart
    # Remove the item from the session or database
    pass

@app.route('/checkout')
@login_required
def checkout():
    # Logic to process the checkout
    # Calculate the total price, update inventory, create rental records, etc.
    pass

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