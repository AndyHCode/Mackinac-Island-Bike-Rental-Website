import sqlite3
import os
from .hashing import hashPassword, verifyPassword
databaseLocation = "./mainDatabase.db"

def createDatabase():
    # Create the database tables if they don"t exist
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bikes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        price_per_hour REAL NOT NULL,
        availability INTEGER NOT NULL,
        image_path TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY,
        bike_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        start_date DATETIME NOT NULL,
        end_date DATETIME NOT NULL,
        total_price REAL NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bike_id) REFERENCES bikes(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0)
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL DEFAULT 0
    )
    """)
    
    cursor.execute("""
    SELECT COUNT(*) FROM earnings
    """)
    count = cursor.fetchone()[0]

    # If no earnings record exists, insert a default amount
    if count == 0:
        cursor.execute("""
        INSERT INTO earnings (amount) VALUES (?)
        """, (0,))

    connection.commit()
    connection.close()
    

def createUser(username, email, password):
    # Create a new user 
    password_hash = hashPassword(password)
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    # Check if any users exist in the database
    cursor.execute("""
    SELECT COUNT(*) FROM users
    """)
    count = cursor.fetchone()[0]
    # If no users exist, assign admin privileges
    if count == 0:  
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, 1))  
    # else, assign customer privileges
    else:  
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, 0))

    connection.commit()
    connection.close()
    
    
def checkLogin(username, password):
    # Check if a user"s login credentials are valid
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT password_hash FROM users
    WHERE username = ?
    """, (username,))

    stored_hashed_password = cursor.fetchone()
    if stored_hashed_password:
        return verifyPassword(password, stored_hashed_password[0])

    connection.close()

    return False

def deleteUser(username):
    # Delete a user
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM users
    WHERE username = ?
    """, (username,))

    connection.commit()
    connection.close()
    
def updateBikeAvailability(bike_id, availability):
    # Update the availability of a bike in the database
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    UPDATE bikes
    SET availability = ?
    WHERE id = ?
    """, (availability, bike_id))

    connection.commit()
    connection.close()

def addRental(bike_id, user_id, start_date, end_date, total_price):
    # Add a new rental entry to the database
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO rentals (bike_id, user_id, start_date, end_date, total_price)
    VALUES (?, ?, ?, ?, ?)
    """, (bike_id, user_id, start_date, end_date, total_price))

    connection.commit()
    connection.close()

def addBike(name, type, pricePerHour, availability, image_path):
    # Add a new bike to the database
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO bikes (name, type, price_per_hour, availability, image_path)
    VALUES (?, ?, ?, ?, ?)
    """, (name, type, pricePerHour, availability, image_path))

    connection.commit()
    connection.close()

def removeBike(bike_id):
    # Remove a bike from the database along with its image file
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    # Get the image path of the bike
    cursor.execute("SELECT image_path FROM bikes WHERE id = ?", (bike_id,))
    image_path = cursor.fetchone()[0]

    # Remove the image file if it exists
    if image_path:
        os.remove("src/static/uploads/"+image_path)

    # Remove the bike from the database
    cursor.execute("DELETE FROM bikes WHERE id = ?", (bike_id,))

    connection.commit()
    connection.close()

def printListBikes():
    # Print out a list of bikes from the database
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, name, type, price_per_hour, availability FROM bikes
    """)

    bikes = cursor.fetchall()

    print("List of Bikes:")
    for bike in bikes:
        print(f"ID: {bike[0]}, Name: {bike[1]}, Type: {bike[2]}, Price Per Hour: {bike[3]}, Availability: {bike[4]}")

    connection.close()

def getListBikes():
    # Get the list of bikes from the database
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, name, type, price_per_hour, availability, image_path FROM bikes
    """)

    bikes = cursor.fetchall()

    connection.close()

    return bikes
    
def getUserInfoByUsername(username):
    # Get user information by username
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, username, email, password_hash, is_admin FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password": user[3],
            "is_admin": user[4]
            
        }
    else:
        return None
    
def getUserById(userId):
    # Get user information by user ID
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, username, email, password_hash, is_admin FROM users
    WHERE id = ?
    """, (userId,))

    user = cursor.fetchone()

    connection.close()
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password_hash": user[3],
            "is_admin": user[4]
        }
    else:
        return None
def getBikeById(bike_id):
    # Get bike information by bike ID."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, name, type, price_per_hour, availability, image_path FROM bikes
    WHERE id = ?
    """, (bike_id,))

    bike = cursor.fetchone()

    connection.close()

    if bike:
        return {
            "id": bike[0],
            "name": bike[1],
            "type": bike[2],
            "price_per_hour": bike[3],
            "availability": bike[4],
            "image_path": bike[5]
        }
    else:
        return None

def getAvailableBikeCount(bike_id):
    """Get the count of available bikes by bike ID."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT availability FROM bikes
    WHERE id = ?
    """, (bike_id,))

    availability = cursor.fetchone()

    connection.close()

    if availability:
        return availability[0]  # Return the count of available bikes
    else:
        return 0  # If bike does not exist, return 0
    
import sqlite3

def printRentedBikes():
    # Print out all rented bikes
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT rentals.id, bikes.name, rentals.start_date, rentals.end_date, rentals.user_id
    FROM rentals
    INNER JOIN bikes ON rentals.bike_id = bikes.id
    """)

    rented_bikes = cursor.fetchall()

    print("Rented Bikes:")
    for bike in rented_bikes:
        print(f"Rental ID: {bike[0]}, Bike Name: {bike[1]}, Start Date: {bike[2]}, End Date: {bike[3]}, User ID: {bike[4]}")

    connection.close()

def getRentedBikes(user_id):
    # Get the list of bikes rented by a specific user
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    # Select rented bikes for the given user ID
    cursor.execute("""
    SELECT bikes.id, bikes.name, bikes.image_path, rentals.start_date, rentals.end_date, rentals.id as rental_id
    FROM bikes
    INNER JOIN rentals ON bikes.id = rentals.bike_id
    WHERE rentals.user_id = ?
    """, (user_id,))

    rented_bikes = cursor.fetchall()

    connection.close()

    bikes_info = []
    for bike in rented_bikes:
        bikes_info.append({
            "id": bike[0],
            "name": bike[1],
            "image_path": bike[2],
            "start_date": bike[3],
            "end_date": bike[4],
            "rental_id": bike[5]
        })

    return bikes_info


def returnRent(rental_id):
    # Remove the rented bike from the rental list and increase the count in the bike table
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("SELECT bike_id FROM rentals WHERE id = ?", (rental_id,))
    bike_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM rentals WHERE id = ?", (rental_id,))

    cursor.execute("UPDATE bikes SET availability = availability + 1 WHERE id = ?", (bike_id,))

    connection.commit()
    connection.close()


def addEarnings(amount):
    # Add earnings to the total amount
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    UPDATE earnings
    SET amount = amount + ?
    """, (amount,))

    connection.commit()
    connection.close()

def clearEarnings():
    # Clear the total amount of earnings
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    UPDATE earnings
    SET amount = 0
    """)

    connection.commit()
    connection.close()

def getEarnings():
    # Get the total amount of earnings
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT amount FROM earnings
    """)
    
    earnings = cursor.fetchone()[0]
    connection.close()

    return earnings

def checkUserByUsername(username):
    # Get a user by username
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    return user
def checkUserByEmail(email):
    # Get a user by email
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    connection.close()
    return user
 