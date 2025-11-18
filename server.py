from flask import Flask, jsonify, request
import sqlite3
from datetime import date

app = Flask(__name__)

# constant
DB_NAME = "budget_manager.db"


def init_db():
    conn = sqlite3.connect(DB_NAME) # opens a connection to the database file named budget_manager.db
    cursor = conn.cursor() # creates a cursor/tool that lets us send commands (SELECT, INSERT, ...)

    #----- user table -----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     username TEXT UNIQUE NOT NULL,
     password TEXT NOT NULL
    )
    """)


    #----- expense table -----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     title TEXT,
     description TEXT NOT NULL,
     amount TEXT NOT NULL,
     date TEXT NOT NULL,
     category TEXT NOT NULL,
     user_id INTEGER,
     FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit() # Save changes to the database
    conn.close() # Close the connection to the database



@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200


@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)  # open a connection to the database
    cursor = conn.cursor()  # create a cursor/tool (SELECT, INSERT, ...)

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) # Executes the SQL statement
    conn.commit() # Save changes to the database
    conn.close() # Close the connection to the database

    return jsonify({
        "success": True,
        "message": "User registered successfully"
    }), 201

@app.post("/api/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME) 
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username,password))
    user = cursor.fetchone()  
    conn.close()  

    if user and user["password"] == password:
        return jsonify({
            "user_id": user["id"],
            "username": user["username"]
        }), 200

    return jsonify({
        "success": False,
        "message": "User not found or incorrect password"
    }), 404

@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect(DB_NAME) 
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()  
    conn.close()  

    if user:
        return jsonify({
            "id": user["id"],
            "username": user["username"]
        }), 200

    return jsonify({
        "success": False,
        "message": "User not found"
    }), 404

@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    conn.commit() 
    conn.close() 

    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200

@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit() 
    conn.close() 

    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200

@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME) 
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()  
    conn.close()  

    users = []
    for row in rows:
        users.append({
            "id": row["id"],
            "username": row["username"],
            "password": row["password"]
        })

    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200


#-----expense endpoints would go here -----
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date_str = date.today()
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)  
    cursor = conn.cursor()  

    cursor.execute("""
    INSERT INTO expenses (title, description, amount, date, category, user_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, amount, date_str, category, user_id))

    conn.commit()  
    conn.close()  

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
