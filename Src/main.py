from flask import Flask, render_template, request, redirect, url_for
import sys, os
sys.path.append(os.path.relpath("./db"))
from database import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if checkLogin(username, password):
            # User authenticated, redirect to store page
            return redirect(url_for('store'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # You may want to add more validation here
        createUser(username, email, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/store')
def store():
    # Add logic to retrieve and display bikes from the database
    return render_template('store.html')

if __name__ == '__main__':
    createDatabase()
    app.run(debug=True)
