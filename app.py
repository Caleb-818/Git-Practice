import sqlite3



def get_connection():
    connection = sqlite3.connect('database.db')
    return connection

def init_db():
    connection = get_connection()
    with open('schema.sql', 'r') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


init_db()

connection = get_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM USERS")
results = cursor.fetchall()

if results:
    for row in results:
            print(row)
else:
     print("No rows yet.")






connection.close()
