from flask import jsonify
from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = 'some-idiot-told-me-to-change-this'

@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip().lower()
    conn = get_db_connection()
    suggestions = []
    if query and conn:
        rows = conn.execute('SELECT * FROM products WHERE stock > 0 AND LOWER(name) LIKE ?', (f'%{query}%',)).fetchall()
        for row in rows:
            suggestions.append({
                'id': row['id'],
                'name': row['name'],
                'image': row['image'],
                'original_artist': row['original_artist'],
                'price': row['price'],
                'painting_orientation': row['painting_orientation'],
                'price_range': row['price_range'],
                'date_category': row['date_category'],
                'art_movement': row['art_movement'],
                'painting_type': row['painting_type']
            })
        conn.close()
    return jsonify(suggestions)

@app.route('/product/<int:product_id>')
def single_product_view(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        return redirect(url_for('storefront'))
    return render_template('Product_Display_Pages/single_product_view.html', product=product)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    conn = get_db_connection()
    results = []
    if query and conn:
        rows = conn.execute('SELECT * FROM products WHERE stock > 0 AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(original_artist) LIKE ?)', (f'%{query.lower()}%', f'%{query.lower()}%', f'%{query.lower()}%')).fetchall()
        for row in rows:
            results.append(dict(row))
        conn.close()
    return render_template('Search_And_Storefront_Pages/main_search_results.html', results=results, search_term=query)


@app.route('/admin/add_product', methods=['GET', 'POST'])
def admin_add_product_page():
    if not session.get('user') or not session.get('is_admin'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        original_artist = request.form['original_artist']
        price = float(request.form['price'])
        image = request.form.get('image', '')
        painting_orientation = request.form.get('painting_orientation', '')
        price_range = request.form.get('price_range', '')
        date_category = request.form.get('date_category', '')
        art_movement = request.form.get('art_movement', '')
        painting_type = request.form.get('painting_type', '')
        stock = int(request.form.get('stock', 1))
        description = request.form.get('description', '')

        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            image = image_file.filename
            product_images_path = os.path.join('static', 'Product_Images', image)
            image_file.save(product_images_path)

        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, original_artist, price, image, painting_orientation, price_range, date_category, art_movement, painting_type, stock, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (name, original_artist, price, image, painting_orientation, price_range, date_category, art_movement, painting_type, stock, description))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    return render_template('Admin_Pages/add_product.html')

@app.route('/admin/edit_product/<int:product_id>', methods=['GET'])
def admin_edit_product_page(product_id):
    if not session.get('user') or not session.get('is_admin'):
        return redirect(url_for('index'))
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        return redirect(url_for('admin_panel'))
    return render_template('Admin_Pages/edit_product.html', product=product)
    
@app.route('/terms')
def terms():
    return render_template('User_Authentication_Pages/terms_and_conditions.html')

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    featured_products = random.sample(products, min(3, len(products)))
    return render_template('homepage.html', products=products, featured_products=featured_products)

@app.route('/storefront')
def storefront():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE stock > 0').fetchall()
    conn.close()
    return render_template('Product_Display_Pages/storefront.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_url = request.form.get('redirect_referrer') or request.args.get('next') or request.referrer or url_for('index')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            session['first_name'] = user['first_name'] if 'first_name' in user.keys() else ''
            session['last_name'] = user['last_name'] if 'last_name' in user.keys() else ''
            session['is_admin'] = bool(user['admin']) if 'admin' in user.keys() else False
            # Redirect to next_url if not login or signup page, else to index
            if next_url and ('/login' not in next_url and '/signup' not in next_url):
                return redirect(next_url)
            else:
                return redirect(url_for('index'))
        else:
            error = 'Invalid credentials.'
    return render_template('User_Authentication_Pages/login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session.pop('is_admin', None)
    next_url = request.referrer or url_for('index')
    if next_url and ('/login' not in next_url and '/signup' not in next_url):
        return redirect(next_url)
    else:
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    next_url = request.form.get('redirect_referrer') or request.referrer or url_for('index')
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
                hashed_pw = generate_password_hash(password)
                conn.execute('INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                             (email, hashed_pw, first_name, last_name))
                conn.commit()
                # Fetch the new user to check admin status (should be False by default)
                user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
                conn.close()
                session['user'] = email
                session['first_name'] = user['first_name'] if user and 'first_name' in user.keys() else ''
                session['last_name'] = user['last_name'] if user and 'last_name' in user.keys() else ''
                session['is_admin'] = bool(user['admin']) if user and 'admin' in user.keys() else False
                # Redirect to next_url if not login or signup page, else to index
                if next_url and ('/login' not in next_url and '/signup' not in next_url):
                    return redirect(next_url)
                else:
                    return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                error = 'Email already registered.'
            conn.close()
    return render_template('User_Authentication_Pages/signup.html', error=error)

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
    
    return render_template('Item_Purchase_Pages/cart.html', 
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




@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('user'):
        return redirect(url_for('login'))
    import json
    from datetime import datetime
    cart_items = session.get('cart', [])
    # POST: Record order, set stock to zero for all products in cart
    if request.method == 'POST':
        if cart_items:
            conn = get_db_connection()
            # Set stock to zero
            for item in cart_items:
                conn.execute('UPDATE products SET stock = 0 WHERE id = ?', (item['product_id'],))
            # Prepare order data
            user_email = session.get('user')
            user = conn.execute('SELECT * FROM users WHERE email = ?', (user_email,)).fetchone() if user_email else None
            user_id = user['id'] if user else None
            address = ', '.join([
                request.form.get('street', ''),
                request.form.get('city', ''),
                request.form.get('state', ''),
                request.form.get('zip', ''),
                request.form.get('country', '')
            ])
            items = []
            total_cost = 0
            for item in cart_items:
                product = conn.execute('SELECT * FROM products WHERE id = ?', (item['product_id'],)).fetchone()
                if product:
                    items.append({
                        'product_id': product['id'],
                        'name': product['name'],
                        'quantity': item['quantity'],
                        'price': product['price']
                    })
                    total_cost += product['price'] * item['quantity']
            # Insert order
            conn.execute('''
                INSERT INTO orders (user_id, order_time, total_cost, address, items)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                datetime.now().isoformat(),
                total_cost,
                address,
                json.dumps(items)
            ))
            conn.commit()
            conn.close()
            session['cart'] = []
        return render_template('Item_Purchase_Pages/checkout_confirmation.html')
    # GET: Show checkout form
    total_amount = 0
    if cart_items:
        conn = get_db_connection()
        for item in cart_items:
            product = conn.execute('SELECT * FROM products WHERE id = ?', (item['product_id'],)).fetchone()
            if product:
                subtotal = product['price'] * item['quantity']
                total_amount += subtotal
        conn.close()
    tax_amount = total_amount * 0.10
    final_total = total_amount + tax_amount
    user_email = session.get('user', '')
    first_name = session.get('first_name', '')
    last_name = session.get('last_name', '')
    return render_template('Item_Purchase_Pages/checkout.html', total_cost="{:.2f}".format(final_total), user_email=user_email, first_name=first_name, last_name=last_name)

@app.route('/admin')
def admin_panel():
    if not session.get('user') or not session.get('is_admin'):
        return redirect(url_for('index'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('Admin_Pages/admin_table.html', products=products)




@app.route('/admin/edit/<int:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    if not session.get('user') or not session.get('is_admin'):
        return redirect(url_for('index'))

    name = request.form['name']
    original_artist = request.form['original_artist']
    price = float(request.form['price'])
    painting_orientation = request.form.get('painting_orientation', '')
    price_range = request.form.get('price_range', '')
    date_category = request.form.get('date_category', '')
    art_movement = request.form.get('art_movement', '')
    painting_type = request.form.get('painting_type', '')
    stock = int(request.form.get('stock', 1))
    description = request.form.get('description', '')

    image = request.form.get('current_image', '')
    if 'image' in request.files and request.files['image'].filename:
        image_file = request.files['image']
        image = image_file.filename
        product_images_path = os.path.join('static', 'Product_Images', image)
        image_file.save(product_images_path)

    conn = get_db_connection()
    conn.execute('''
        UPDATE products SET
            name=?,
            original_artist=?,
            price=?,
            image=?,
            painting_orientation=?,
            price_range=?,
            date_category=?,
            art_movement=?,
            painting_type=?,
            stock=?,
            description=?
        WHERE id=?
    ''', (name, original_artist, price, image, painting_orientation, price_range, date_category, art_movement, painting_type, stock, description, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('user') or not session.get('is_admin'):
        return redirect(url_for('index'))
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

import sys
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clear_users':
            conn = get_db_connection()
            conn.execute("DELETE FROM users WHERE admin IS NULL OR admin = 0")
            conn.commit()
            conn.close()
            print('All non-admin user data cleared from users table.')
        elif sys.argv[1] == 'make_admin':
            if len(sys.argv) < 3:
                print('Usage: python app.py make_admin <email>')
                sys.exit(1)
            email = sys.argv[2]
            conn = get_db_connection()
            conn.execute("UPDATE users SET admin = 1 WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            print(f'User {email} set as admin.')
        else:
            print('Unknown debug command.')
    else:
        app.run(debug=True)

