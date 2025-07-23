from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY, user TEXT, event TEXT, date TEXT, seat TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('booking.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash('Account created! Please login.')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('booking.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    all_seats = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']

    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE user=?", (session['user'],))
    bookings = c.fetchall()

    # Fetch already booked seats for today
    c.execute("SELECT seat FROM bookings WHERE date = date('now')")
    booked = [row[0] for row in c.fetchall()]
    conn.close()

    available_seats = [s for s in all_seats if s not in booked]

    return render_template('dashboard.html', user=session['user'], bookings=bookings, seats=available_seats)

@app.route('/book', methods=['POST'])
def book():
    if 'user' not in session:
        return redirect('/login')
    event = request.form['event']
    date = request.form['date']
    seat = request.form['seat']

    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE date=? AND seat=?", (date, seat))
    if c.fetchone():
        conn.close()
        flash(f"Seat {seat} is already booked for this date!")
        return redirect('/dashboard')
    
    c.execute("INSERT INTO bookings (user, event, date, seat) VALUES (?, ?, ?, ?)", (session['user'], event, date, seat))
    conn.commit()
    conn.close()
    flash('Ticket booked successfully!')
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
