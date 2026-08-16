import sqlite3
from flask import Flask

#Creating the flask application object. Every route, template and configuration attaches to this object.

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)





