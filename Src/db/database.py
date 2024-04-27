import sqlite3
import os
from .hashing import hashPassword, verifyPassword
databaseLocation = "./mainDatabase.db"


def createDatabase():
    """Create the database tables if they don't exist."""
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

    connection.commit()
    connection.close()

def createUser(username, email, password):
    """Create a new user."""
    password_hash = hashPassword(password)
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    # Check if any users exist in the database
    cursor.execute("""
    SELECT COUNT(*) FROM users
    """)
    count = cursor.fetchone()[0]

    if count == 0:  # If no users exist, assign admin privileges
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, 1))  # 1 represents admin privilege
    else:  # Otherwise, assign customer privileges
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, 0))  # 0 represents customer privilege

    connection.commit()
    connection.close()
    
    

def checkLogin(username, password):
    """Check if a user's login credentials are valid."""
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
    """Delete a user."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM users
    WHERE username = ?
    """, (username,))

    connection.commit()
    connection.close()

def addBike(name, type, pricePerHour, availability, image_path):
    """Add a new bike to the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO bikes (name, type, price_per_hour, availability, image_path)
    VALUES (?, ?, ?, ?, ?)
    """, (name, type, pricePerHour, availability, image_path))

    connection.commit()
    connection.close()

def removeBike(bike_id):
    """Remove a bike from the database along with its image file."""
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
    """Print out a list of bikes from the database."""
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
    """Get the list of bikes from the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, name, type, price_per_hour, availability, image_path FROM bikes
    """)

    bikes = cursor.fetchall()

    connection.close()

    return bikes
    
def getUserByUsername(username, password):
    """Get user information by username."""
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
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password': user[3],
            'is_admin': user[4]
            
        }
    else:
        return None
    
def getUserById(userId):
    """Get user information by user ID."""
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
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password_hash': user[3],
            'is_admin': user[4]
        }
    else:
        return None
def getBikeById(bike_id):
    """Get bike information by bike ID."""
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
            'id': bike[0],
            'name': bike[1],
            'type': bike[2],
            'price_per_hour': bike[3],
            'availability': bike[4],
            'image_path': bike[5]
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

