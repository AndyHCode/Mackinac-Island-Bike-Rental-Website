import sqlite3

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
        availability INTEGER NOT NULL
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
        password_hash TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()


def createUser(username, email, passwordHash):
    """Create a new user."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO users (username, email, password_hash)
    VALUES (?, ?, ?)
    """, (username, email, passwordHash))

    connection.commit()
    connection.close()


def checkLogin(username, passwordHash):
    """Check if a user's login credentials are valid."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM users
    WHERE username = ? AND password_hash = ?
    """, (username, passwordHash))

    user = cursor.fetchone()

    connection.close()

    return user is not None


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

def addBike(name, type, pricePerHour, availability):
    """Add a new bike to the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO bikes (name, type, price_per_hour, availability)
    VALUES (?, ?, ?, ?)
    """, (name, type, pricePerHour, availability))

    connection.commit()
    connection.close()


def removeBike(bike_id):
    """Remove a bike from the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM bikes
    WHERE id = ?
    """, (bike_id,))

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

def addRental(bike_id, user_id, start_date, end_date, total_price):
    """Add a new rental to the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO rentals (bike_id, user_id, start_date, end_date, total_price)
    VALUES (?, ?, ?, ?, ?)
    """, (bike_id, user_id, start_date, end_date, total_price))

    connection.commit()
    connection.close()

def removeRental(rental_id):
    """Remove a rental from the database."""
    connection = sqlite3.connect(databaseLocation)
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM rentals
    WHERE id = ?
    """, (rental_id,))

    connection.commit()
    connection.close()