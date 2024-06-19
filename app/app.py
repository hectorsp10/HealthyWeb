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

if __name__ == '_main_':
    app.run(debug=True)