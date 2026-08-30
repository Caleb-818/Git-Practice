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
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return "Username and Password are required."

    hashed = generate_password_hash(password)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO USERS (username, password_hash) VALUES (?, ?)",
            (username, hashed)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        return "That username is already taken"

    connection.close()
    return redirect(url_for('register'))


@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method =='GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USERS WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    if user is None or not check_password_hash(user['password_hash'], password):
        return "Invalid username or password"

    session['user_id'] = user['id']
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)





