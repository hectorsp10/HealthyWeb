from flask import Flask, render_template, request, g
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

#git commit -m "mensaje"

app = Flask(__name__)
database = 'healthy.db'

#database connection
def get_db():
    db = getattr(g, '_healthy', None)
    if db is None:
        db = g._healthy = sqlite3.connect(database)
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html")
        
        elif not request.form.get("password"):
            return render_template("register.html")

        username = request.form.get("username")
        password = request.form.get("password")
        comfirmation = request.form.get("comfirmation")

        if password:
            if password == comfirmation:
                passwordHash = generate_password_hash(password)
                
                # query database to check if passwordHash exists

    else:
        return render_template("register.html")

if __name__ == '_main_':
    app.run(debug=True)