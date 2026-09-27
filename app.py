import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                section TEXT NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                is_secondhand INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                book_title TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM books")
        if cur.fetchone()[0] == 0:
            cur.executemany('''
                INSERT INTO books (isbn, title, author, section, stock_quantity, is_secondhand)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', [
                ('978-0141', 'The Great Gatsby', 'F. Scott', 'Fiction', 5, 0),
                ('978-0061', 'To Kill a Mockingbird', 'Harper Lee', 'Classics', 3, 0),
                ('SH-001', '1984 (Annotated)', 'George Orwell', 'Secondhand', 1, 1)
            ])
        conn.commit()

@app.route('/')
def index():
    section = request.args.get('section', '')
    with get_db() as conn:
        if section:
            books = conn.execute('SELECT * FROM books WHERE section = ?', (section,)).fetchall()
        else:
            books = conn.execute('SELECT * FROM books').fetchall()
        orders = conn.execute('SELECT * FROM orders').fetchall()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Bellbird Books Portal</title><style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f4f6f8; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #004b87; color: white; }
    </style></head>
    <body>
        <h1>Bellbird Books - Inventory & Click-and-Collect</h1>
        <div class="card">
            <h3>Filter Inventory by Section</h3>
            <form method="get">
                <input type="text" name="section" placeholder="e.g. Fiction, Classics..." value="{{ section }}">
                <button type="submit">Filter</button> <a href="/">Reset</a>
            </form>
            <table>
                <tr><th>ISBN/ID</th><th>Title</th><th>Author</th><th>Section</th><th>Stock</th><th>Type</th></tr>
                {% for b in books %}
                <tr><td>{{ b.isbn }}</td><td>{{ b.title }}</td><td>{{ b.author }}</td><td>{{ b.section }}</td><td>{{ b.stock_quantity }}</td><td>{{ 'Secondhand' if b.is_secondhand else 'New' }}</td></tr>
                {% else %}
                <tr><td colspan="6">No books found in this section (Empty list).</td></tr>
                {% endfor %}
            </table>
        </div>
        <div class="card">
            <h3>Special Out-of-Stock Order Registration</h3>
            <form action="/order" method="post">
                <input type="text" name="customer_name" placeholder="Customer Name" required>
                <input type="text" name="phone" placeholder="Phone" required>
                <input type="text" name="book_title" placeholder="Requested Book Title" required>
                <button type="submit">Submit Special Order</button>
            </form>
            <h4>Pending Special Orders:</h4>
            <table>
                <tr><th>ID</th><th>Customer</th><th>Phone</th><th>Requested Title</th><th>Status</th></tr>
                {% for o in orders %}
                <tr><td>{{ o.id }}</td><td>{{ o.customer_name }}</td><td>{{ o.phone }}</td><td>{{ o.book_title }}</td><td><b>{{ o.status }}</b></td></tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, books=[dict(b) for b in books], orders=[dict(o) for o in orders], section=section)

@app.route('/order', methods=['POST'])
def create_order():
    c_name = request.form['customer_name']
    phone = request.form['phone']
    title = request.form['book_title']
    with get_db() as conn:
        conn.execute("INSERT INTO orders (customer_name, phone, book_title, status) VALUES (?, ?, ?, 'Pending')",
                     (c_name, phone, title))
        conn.commit()
    return '<script>alert("Special order created successfully with status: Pending!"); window.location.href="/";</script>'

if __name__ == '__main__':
    init_db()
    app.run(port=5000)
