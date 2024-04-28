from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
from werkzeug.utils import secure_filename
import sys, os
sys.path.append(os.path.relpath("./db"))
import db
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)

# hold user login data when user sign in
class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin
# load the user data
@login_manager.user_loader
def load_user(userId):
    user = db.getUserById(userId)
    if user:
        return User(userId, user["username"], user.get("is_admin", False))

#home page
@app.route("/")
def index():
    db.printRentedBikes()
    return render_template("index.html")
# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # if user is login, route them to the store page
    if current_user.is_authenticated:
        return redirect(url_for("store"))
    # login form, load check login and load user object
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.getUserInfoByUsername(username)
        if user and db.checkLogin(username, password):
            userObj = User(user["id"], username)
            userObj.username = user["username"]
            login_user(userObj)
            return redirect(url_for("store"))
        else:
            error = "Invalid username or password"
            return render_template("login.html", error=error)
    return render_template("login.html")
# sign up page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # redirect user to store page if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("store"))
    error = None
    
    # create user account
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        # Check if the username or email already exists in the database
        existing_user = db.checkUserByUsername(username)
        existing_email = db.checkUserByEmail(email)
        
        if existing_user:
            error = "Username already exists. Please choose a different one."
            return render_template("signup.html", error=error)
        elif existing_email:
            error = "Email already exists. Please use a different email."
            return render_template("signup.html", error=error)
        else:
            # Create user if username and email are unique
            db.createUser(username, email, password)
            return redirect(url_for("login"))
    
    return render_template("signup.html", error=error)

# store page
@app.route("/store")
def store():
    # error handling
    error = request.args.get("error")
    # get list of bikes and send them to the html page
    bikes = db.getListBikes()
    return render_template("store.html", bikes=bikes, error=error)

# logout call, clear user obj and clear session, and redirect them to index/home page
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))
# add bike to cart call
@app.route("/add_to_cart/<string:bike_id>", methods=["POST"])
def add_to_cart(bike_id):
    # Retrieve the current cart from the session
    cart = session.get("cart", [])
    
    # Get number of bike count from the database
    available_count = db.getAvailableBikeCount(bike_id)
    counter = 0
    # count number of bikes in cart
    for x in cart:
        if x.get("bike_id") == bike_id:
            counter = counter + 1
    # check if bike in cart is over database bike
    if counter == available_count:
        error = "Exceeded available bike count"
        return redirect(url_for("store", error=error))
    else:
        cart.append({"bike_id": bike_id, "hours": 1})
        # Store the updated cart back into the session
        session["cart"] = cart
        
        # Redirect the user back to the store page
        return redirect(url_for("store", error=None))

# view cart page
@app.route("/view_cart")
def view_cart():
    # Get the current cart from the session
    cart = session.get("cart", [])
    
    # Initialize a list to store cart items with bike details
    cart_items = []
    total_price = 0
    
    # Loop through items in the cart
    for x in cart:
        # Retrieve bike information from the database based on bike_id
        bike = db.getBikeById(x["bike_id"])
        
        # Check if the bike exists
        if bike:
            # Calculate the total price for the item
            item_total_price = bike["price_per_hour"] * x["hours"]
            
            # Add the item with bike details to the cart_items list
            cart_items.append({
                "bike": bike,
                "hours": x["hours"],
                "total_price": item_total_price
            })
            
            # Update the total price
            total_price += item_total_price
    
    # Render the cart template with cart items and total price
    return render_template("cart.html", cart=cart_items, total_price=total_price)

# update cart call
@app.route("/update_cart/<int:index>", methods=["POST"])
def update_cart(index):
    # get the current cart from the session
    cart = session.get("cart", [])
    
    # get the updated hours from the form
    updated_hours = int(request.form["hours"])
    
    # get the price per hour of the bike from the database
    bike_id = cart[index]["bike_id"]
    bike = db.getBikeById(bike_id)
    price_per_hour = bike["price_per_hour"]
    
    # Update the hours for the item in the cart
    cart[index]["hours"] = updated_hours
    
    # Update the total price for the item
    cart[index]["total_price"] = price_per_hour * updated_hours
    
    # Store the updated cart back into the session
    session["cart"] = cart
    
    return redirect(url_for("view_cart"))

# delete bike from cart call
@app.route("/delete_bike_cart/<int:index>", methods=["POST"])
def delete_bike_cart(index):
    # get the current cart from the session
    cart = session.get("cart", [])
    
    # Remove the bike at the index from the cart
    del cart[index]
    
    # Store the updated cart back into the session
    session["cart"] = cart
    
    return redirect(url_for("view_cart"))

def creditCardChecker(cardNumber, cvv, expiryDate):
    # For this project, we"ll assume any card number with 16 digits is valid
    if len(cardNumber) != 16:
        return False

    # we"ll also assume CVV must be 3 digits
    if len(cvv) != 3 or not cvv.isdigit():
        return False

    # Check if expiry date is in the format MM/YY and is not expired
    try:
        expiryMonth, expiryYear = map(int, expiryDate.split("/"))
        expiryDate = datetime(year=2000 + expiryYear, month=expiryMonth, day=1)
        currentDate = datetime.now()
        if expiryDate < currentDate:
            return False
    except:
        return False

    return True

# checkout page
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", [])
    if cart == []:
        return redirect(url_for("view_cart"))
    cart_items = []
    total_price = 0
    error = None
    # Loop through items in the cart
    for x in cart:
        # Retrieve bike information from the database based on bike_id
        bike = db.getBikeById(x["bike_id"])
        
        # Check if the bike exists
        if bike:
            # Calculate the total price for the item
            item_total_price = bike["price_per_hour"] * x["hours"]
            
            # Add the item with bike details to the cart_items list
            cart_items.append({
                "bike": bike,
                "hours": x["hours"],
                "total_price": item_total_price
            })
            
            # Update the total price
            total_price += item_total_price
    if request.method == "POST":
         # Retrieve credit card number from the form
        creditCardNumber = request.form.get("card_number")
        cvv = request.form.get("cvv")
        expiryDate = request.form.get("expiry_date")

        # check the credit card number
        if creditCardChecker(creditCardNumber, cvv, expiryDate):
            # add earnings to database
            db.addEarnings(total_price)
            cart = session.get("cart", [])
            # add bike rented to database and decrease the amount of bikes database
            for x in cart:
                bike_id = x["bike_id"]
                availability = db.getAvailableBikeCount(bike_id) - 1
                db.updateBikeAvailability(bike_id, availability)
                start_date = datetime.now().strftime("%m-%d-%Y %I:%M %p")
                end_date = (datetime.now() + timedelta(hours=x["hours"])).strftime("%m-%d-%Y %I:%M %p")
                db.addRental(bike_id,current_user.id, start_date, end_date, total_price) 
            # clear cart 
            session.pop("cart", None)
            

            return redirect(url_for("thank_you"))
        else:
            # if the Payment fails, print out error
            error = "Invalid credit card number. Please try again."
            return render_template("checkout.html", error=error, cart=cart_items, total_price=total_price)
    return render_template("checkout.html",error=error, cart=cart_items, total_price=total_price)

# thank you page
@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")


# return bike page
@app.route("/return_bike", methods=["GET", "POST"])
@login_required
def return_bike():
    if request.method == "POST":
        # Get the rental ID from the form submission
        rental_id = request.form.get("rental_id")
        # Handle the return of the bike with the given rental ID
        # Update the database to mark the bike as returned
        db.printRentedBikes()
        db.returnRent(rental_id)
        # Redirect to the return_bike page to refresh the list of rented bikes
        return redirect(url_for("return_bike"))

    # Retrieve the list of rented bikes for the current user from the database
    rented_bikes = db.getRentedBikes(current_user.id)
    print(rented_bikes)

    # Render the return_bike.html template with the rented bikes data
    return render_template("return_bike.html", rented_bikes=rented_bikes)

# admin page
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    # check if user is a admin
    if not current_user.is_admin:
        return "Unauthorized - Only admin users can access this page.", 401
    # form for adding bikes to database 
    if request.method == "POST":
        name = request.form["name"]
        type = request.form["type"]
        price_per_hour = float(request.form["price_per_hour"])
        availability = int(request.form["availability"])
        
        # allow file upload
        file = request.files["image"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        # Add the bike to the database
        db.addBike(name, type, price_per_hour, availability, filename)
        
        return redirect(url_for("admin"))
    
    # get a list of bikes and display them in the admin page
    bikes = db.getListBikes()
    print(bikes)
    
    return render_template("admin.html", bikes=bikes, total_earnings=db.getEarnings())


# clear earnings call
@app.route("/clear_earnings", methods=["POST"])
def clear_Earnings():
    # Clear the money made
    db.clearEarnings()
    return redirect(url_for("admin"))

# remove bike call
@app.route("/remove_bike/<int:bike_id>", methods=["POST"])
@login_required
def remove_bike(bike_id):
    # Remove the bike from the database
    db.removeBike(bike_id)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    db.createDatabase()
    app.config["UPLOAD_FOLDER"] = "src/static/uploads"
    app.run(debug=True)