from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from model import recommend
import sqlite3
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
    return User(id=user[0], username=user[1]) if user else None

# 🔐 Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user[2], password):
            user_obj = User(id=user[0], username=user[1])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

# 🆕 Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        try:
            with sqlite3.connect('users.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
                conn.commit()
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "danger")

    return render_template('signup.html')

# 🚪 Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 🏠 Home with Recommendation + Ratings
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    recommendations = []

    if request.method == 'POST':
        if 'movie' in request.form:
            movie = request.form['movie']
            recommendations = recommend(movie)

        elif 'rating' in request.form:
            movie_title = request.form['movie_title']
            rating = int(request.form['rating'])
            user_id = current_user.id

            with sqlite3.connect('users.db') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO ratings (user_id, movie_title, rating) VALUES (?, ?, ?)",
                            (user_id, movie_title, rating))
                conn.commit()
            flash(f"You rated '{movie_title}' as {rating}/5 ⭐", "success")
            return redirect(url_for('home'))

    return render_template('index.html', recommendations=recommendations, username=current_user.username)

# 🔍 Autocomplete endpoint
@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    try:
        df = pd.read_csv('movies.csv')  # Ensure movies.csv has 'title' and optional 'description'
        matches = df[df['title'].str.lower().str.contains(query, na=False)].head(10)
        results = [
            {
                'title': row['title'],
                'description': row['description'] if 'description' in row else ''
            }
            for _, row in matches.iterrows()
        ]
        return jsonify(results)
    except Exception as e:
        return jsonify([])

# 🧪 Run the app
if __name__ == '__main__':
    app.run(debug=True)
