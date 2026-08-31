import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

#Creating the flask application object. Every route, template and configuration attaches to this object.

app = Flask(__name__)
app.secret_key = 'development'


def get_connection():
    #opens a connection to the sql database file
    connection = sqlite3.connect('database.db')
    #enables access to columns by name instead of position row['username']) instead of (row[1])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    #Runs every SQL statement in schema.sql in order
    connection = get_connection()
    with open('schema.sql', 'r') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


#Make sure the database and tables exist before the app starts dealing with requests
init_db()

#Routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    #GET shows the empty registration form
    if request.method == 'GET':
        return render_template('register.html')


    #POST means the form was submitted so read the values user entered
    username = request.form['username']
    password = request.form['password']

    #Basic server-side check, backs up the required attribute in the HTML
    if not username or not password:
        return "Username and Password are required."

    #Never store the raw password only store the hash
    hashed = generate_password_hash(password)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        #UNIQUE on the username column makes this fail if the username already exists
        cursor.execute(
            "INSERT INTO USERS (username, password_hash) VALUES (?, ?)",
            (username, hashed)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        #Catches the UNIQUE constraint failure instead of letting the app crash
        connection.close()
        return "That username is already taken"

    connection.close()
    return redirect(url_for('register'))


@app.route('/login', methods= ['GET', 'POST'])
def login():
    #GET shows the empty login form
    if request.method =='GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    #Look up the user by username using fetchone because username is UNIQUE
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USERS WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    #Same error message either way, so no need to reveal whether the username exists
    if user is None or not check_password_hash(user['password_hash'], password):
        return "Invalid username or password"

    #Log the user in by storing their id in the session
    session['user_id'] = user['id']
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    #session.get() returns None instead of crashing if user_id isn't set
    user_id = session.get('user_id')

    #If not logged in, send user to login instead of showing dashboard
    if user_id is None:
        return redirect(url_for('login'))

    #If logged in, fetch the user's own data to display
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USERS WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()

    #Pass username into the template so {{ username }} in dashboard.html can use it
    return render_template('dashboard.html', username=user['username'])

@app.route('/logout')
def logout():
    #Remove user_id from the session. None is the safe fallback if it's already missing
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)





