from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions'  # Change this to a random secret key

def get_db_connection():
    conn = sqlite3.connect('missing_artworks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('homepage.html', products=products)

@app.route('/storefront')
def storefront():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('storefront.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user'] = user['email']
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)


# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        import re
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        # Password security checks
        pw_errors = []
        if len(password) < 8:
            pw_errors.append('Password must contain at least 8 characters.')
        if not re.search(r'[A-Z]', password):
            pw_errors.append('Password must contain an uppercase letter.')
        if not re.search(r'[a-z]', password):
            pw_errors.append('Password must contain a lowercase letter.')
        if not re.search(r'[^A-Za-z0-9]', password):
            pw_errors.append('Password must contain a special character.')
        if password != confirm_password:
            error = 'Passwords do not match.'
        elif pw_errors:
            error = pw_errors
        else:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                             (email, password, first_name, last_name))
                conn.commit()
                conn.close()
                session['user'] = email
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                error = 'Email already registered.'
            conn.close()
    return render_template('signup.html', error=error)

@app.route('/cart')
def cart():
    # Get cart items from session
    cart_items = session.get('cart', [])
    
    # Get product details for items in cart
    cart_products = []
    total_amount = 0
    
    if cart_items:
        conn = get_db_connection()
        for item in cart_items:
            product = conn.execute('SELECT * FROM products WHERE id = ?', (item['product_id'],)).fetchone()
            if product:
                cart_product = {
                    'product': dict(product),
                    'quantity': item['quantity'],
                    'subtotal': product['price'] * item['quantity']
                }
                cart_products.append(cart_product)
                total_amount += cart_product['subtotal']
        conn.close()
    
    # Calculate tax (10%)
    tax_amount = total_amount * 0.10
    final_total = total_amount + tax_amount
    
    return render_template('cart.html', 
                         cart_products=cart_products, 
                         subtotal=total_amount,
                         tax=tax_amount,
                         total=final_total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if item already exists in cart
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            break
    else:
        # Add new item to cart
        cart.append({'product_id': product_id, 'quantity': 1})
    
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    
    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if item['product_id'] == product_id:
                if quantity > 0:
                    item['quantity'] = quantity
                else:
                    cart.remove(item)
                break
        session['cart'] = cart
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['product_id'] != product_id]
        session.modified = True
    
    return redirect(url_for('cart'))


# Debug CLI options
import sys
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clear_users':
            conn = get_db_connection()
            conn.execute('DELETE FROM users')
            conn.commit()
            conn.close()
            print('All user data cleared from users table.')
        else:
            print('Unknown debug command.')
    else:
        app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

