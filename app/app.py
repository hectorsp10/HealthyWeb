from flask import Flask, render_template, request, g, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

#git commit -m "mensaje"

app = Flask(__name__)
DATABASE = 'healthy.db'
app.secret_key = 'secretKeY.0394'

#database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

#close conection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        
        if not request.form.get("username"):
            flash('All fields are required, missing username')
            return render_template("register.html")
        
        if not request.form.get("email"):
            flash('All fields are required, missing email')
            return render_template("register.html")
        
        if not request.form.get("password"):
            flash('All fields are required, missing password')
            #return render_template("index.html")
            return render_template("register.html")

        if not request.form.get("confirmation"):
            flash('All fields are required, missing confirmation')
            return render_template("register.html")
        
        if password == confirmation:
            passwordHash = generate_password_hash(password)
                
            # query database to check if passwordHash exists
            db=get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE hash = ?", (passwordHash,))
            checkedPassword = cursor.fetchall()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            checkedEmail = cursor.fetchall()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            checkedUsername = cursor.fetchall()

            if len(checkedPassword) == 0:
                if len(checkedEmail) == 0:
                    if len(checkedUsername) == 0:
                        cursor.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, passwordHash))
                        db.commit()
                        flash('Registered succesfully!')
                        return render_template("register.html")
                    else:
                        flash('Username already exists')
                else:
                    flash('email already exists')
            else:
                flash('Password already exists')
        else:
            flash('Passwords do not match')
            return render_template("register.html")

    else:
        return render_template("register.html")


@app.route('/test_insert')
def test_insert():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, hash) VALUES ('test_user', 'test_hash')")
        db.commit()
        return "Inserted test user."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)