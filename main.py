# https://codeshack.io/login-system-python-flask-mysql/
# from crypt import methods
from datetime import date
from time import time
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime



app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)


# http://localhost:5000/pythonlogin
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
            # return render_template('home.html', username=session['username'])
        else:
            # Account doesnt exist or username/password incorrect
            msg = f'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
    

@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/pythonlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home', methods=['GET', 'POST'])
def home():
    msg=''

    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if request.method == 'POST' and 'name' in request.form and 'date' in request.form and 'type' in request.form and 'time' in request.form and 'seats' in request.form:
            
            name = request.form['name']
            date = request.form['date']            
            type = request.form['type']
            time = request.form['time']            
            seats = request.form['seats']

            if name=='xxx' or date=='xxx' or type=='xxx' or time=='xxx' or seats=='xxx':
                return redirect(url_for('home'))

            date = date.split('-')
            date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
            start_time = time.split("-")[0] + ':00:00'
            end_time = time.split("-")[1].split("p")[0] + ':00:00'

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = 'INSERT INTO tickets VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)'
            values =  (session['id'], name, date, type, start_time, end_time, int(seats),)
            cursor.execute(sql, values)
            mysql.connection.commit()

        elif request.method == 'POST' and 'contact_type' in request.form and 'contact_message' in request.form:
            contact_type = request.form['contact_type']
            contact_message = request.form['contact_message']

            if contact_type=='xxx':
                return redirect(url_for('home'))           

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = 'INSERT INTO reviews VALUES (NULL, %s, %s, %s)'
            values =  (session['id'], contact_type, contact_message, )
            cursor.execute(sql, values)
            mysql.connection.commit()
        
        
    return render_template('home.html')

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        
        cursor.execute('SELECT * FROM tickets WHERE person_id = %s', (session['id'],))
        tickets = cursor.fetchall()

        cursor.execute('SELECT * FROM reviews WHERE person_id = %s', (session['id'],))
        reviews = cursor.fetchall()
        


        # Show the profile page with account info
        return render_template('profile.html', account=account, tickets=tickets, reviews=reviews)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)