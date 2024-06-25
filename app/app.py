from flask import Flask, render_template, request, g, flash, session
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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():

    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    
    if request.method == "POST":

        if not request.form.get("username"):
            flash('please provide username')
            return render_template("login.html")
        
        elif not request.form.get("password"):
            flash('please provide password')
            return render_template("login.html")
        
        #query database for username
        db=get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchall()

        #if the userusername introduced does not match with any registered user
        if len(user) != 1:
            flash('invalid username')
            return render_template("login.html")
        
        if not check_password_hash(user[0]["hash"], password):
            flash('invalid password')
            return render_template("login.html")
    
        #remember the user during the session
        session["user_id"] = user[0]["id"]
        session["user_name"] = user[0]["username"]
        userName = session["user_name"]
        #redirect user to homepage
        return render_template("home.html", user=userName)

    else:
        return render_template("login.html")

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
                        return render_template("login.html")
                    else:
                        flash('Username already exists')
                        return render_template("register.html")
                else:
                    flash('email already exists')
                    return render_template("register.html")
            else:
                flash('Password already exists')
                return render_template("register.html")
        else:
            flash('Passwords do not match')
            return render_template("register.html")

    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)