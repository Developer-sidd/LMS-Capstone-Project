from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'library_user'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'library_db'

mysql = MySQL(app)

def query_db(query, args=(), one=False):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return redirect(url_for('login'))


#login Page Valations for User
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = %s AND password = %s', [username, password], one=True)
        if user:
            session['username'] = username
            session['cart'] = []
            return redirect(url_for('book_management'))
        else:
            return "Incorrect username/password"
    return render_template('login.html')


#Book MAnagament Page with a list of books available
@app.route('/book_management', methods=['GET', 'POST'])
def book_management():
    if 'username' not in session:
        return redirect(url_for('login'))

    book_categories = {
        'Fiction': [
            "To Kill a Mockingbird by Harper Lee",
            "1984 by George Orwell",
            "The Great Gatsby by F. Scott Fitzgerald",
            "Pride and Prejudice by Jane Austen"
        ],
        'Non-Fiction': [
            "Sapiens: A Brief History of Humankind by Yuval Noah Harari",
            "Educated by Tara Westover",
            "Becoming by Michelle Obama",
            "The Immortal Life of Henrietta Lacks by Rebecca Skloot"
        ],
        'Science Fiction': [
            "Dune by Frank Herbert",
            "Neuromancer by William Gibson",
            "The Left Hand of Darkness by Ursula K. Le Guin",
            "Ender's Game by Orson Scott Card"
        ],
        'Fantasy': [
            "The Hobbit by J.R.R. Tolkien",
            "Harry Potter and the Sorcerer's Stone by J.K. Rowling",
            "The Name of the Wind by Patrick Rothfuss",
            "A Game of Thrones by George R.R. Martin"
        ],
        'Mystery/Thriller': [
            "Gone Girl by Gillian Flynn",
            "The Girl with the Dragon Tattoo by Stieg Larsson",
            "The Da Vinci Code by Dan Brown",
            "Big Little Lies by Liane Moriarty"
        ],
        'Horror': [
            "The Shining by Stephen King",
            "Dracula by Bram Stoker",
            "Frankenstein by Mary Shelley",
            "It by Stephen King"
        ],
        'Romance': [
            "Pride and Prejudice by Jane Austen",
            "To Kill a Mockingbird by Harper Lee",
            "One Hundred Years of Solitude by Gabriel García Márquez",
            "The Great Gatsby by F. Scott Fitzgerald"
        ],
    }

    cart = session.get('cart', [])
    if request.method == 'POST':
        selected_books = request.form.getlist('books')
        for book in selected_books:
            if book not in cart:
                cart.append(book)
        session['cart'] = cart
        return redirect(url_for('cart'))

    return render_template('book_management.html', book_categories=book_categories, cart=cart)


#cart management and Date Selection
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if request.method == 'POST':
        start_date = request.form['start_date']
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=30)

        # Exclude weekends
        while end_date.weekday() in [5, 6]:
            end_date += timedelta(days=1)

        session['start_date'] = start_date
        session['end_date'] = end_date

        return redirect(url_for('thank_you'))

    return render_template('cart.html', cart=cart)


#after the cart is created , User Checkout to thank you Page will be displayed 
@app.route('/thank_you')
def thank_you():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    
    return render_template('thank_you.html', start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"))

if __name__ == '__main__':
    app.run(debug=True)
