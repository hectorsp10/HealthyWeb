from flask import Flask, render_template, request, g, flash, session, redirect, url_for
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

    print(username)
    
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
        session['user_id'] = user[0]['id']
        session['user_name'] = user[0]['username']
        userName = session['user_name']
        #redirect user to homepage
        #return render_template("home.html", user=userName)
        return redirect(url_for('home', user=userName))

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

@app.route('/home')
def home():

    if 'user_id' not in session:
        print("user not logged in.")
        return render_template('login.html')

    # query database to know if the current user has already entered their data (height, weight, age, gender, activity_level)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT weight, height, age, gender, activity_level FROM user_stats WHERE user_id = ?", (session['user_id'],))
    user_data = cursor.fetchone()
    print("busca los datos del usuario en la base")

    # if the user has introduced their data
    if user_data:
        #weight = user_data[0]["weight"]
        #height = user_data[0]["height"]
        #age = user_data[0]["age"]
        #gender = user_data[0]["gender"]

        weight, height, age, gender, activity_level = user_data

        print("encuentra los datos del usuario en la base")

        # calory intake calculation
        if gender == 'male': # (male)
            base_cal_intake = 66 + (13.75 * weight) + (5 * height) - (6.75 * age)

        if gender == 'female': # (feale)
            base_cal_intake = 655 + (9.56 * weight) + (1.85 * height) - (4.68 * age)

        return render_template('home.html', user=session["user_name"], base_cal_intake=base_cal_intake, height=height, weight=weight)

    else:
        print("NO encuentra los datos del usuario en la base")
        return render_template('home.html', user=session['user_name'], weight=None, height=None)
    
@app.route("/update", methods=['POST'])
def update():

    weight = request.form.get('weight')
    height = request.form.get('height')
    age = request.form.get('age')
    gender = request.form.get('gender')
    activity = request.form.get('activity')


    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (session['user_id'],))
    user = cursor.fetchall()

    print(weight, height, age, gender, activity)

    if not user:
        cursor.execute("INSERT INTO user_stats (user_id, weight, height, age, gender, activity_level) VALUES (?, ?, ?, ?, ?, ?)", (session['user_id'], weight, height, age, gender, activity,))
        db.commit()
        print("crea los datos del usuario en la base")
        return redirect(url_for('home', user=session['user_name']))
    else:
        cursor.execute("UPDATE user_stats SET weight = ?, height = ?, age = ?, gender = ?, activity_level = ? WHERE user_id = ?", (weight, height, age, gender, activity, session['user_id']))
        db.commit()
        print("sobreescribe los datos del usuario en la base")
        return render_template("home.html", user=session['user_name'])

    
    
    

if __name__ == '__main__':
    app.run(debug=True)