from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_tech_shop'

# Впиши свой пароль от MySQL
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "1234",
    "database": "tech_shop_db"
}

def get_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    cat_id = request.args.get('category', '')

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()

    query = """
        SELECT p.id, p.model, c.name as category, m.name as manufacturer, p.price 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN manufacturers m ON p.manufacturer_id = m.id
        WHERE p.model LIKE %s
    """
    params = [f"%{search}%"]
    if cat_id:
        query += " AND p.category_id = %s"
        params.append(cat_id)

    cur.execute(query, params)
    products = cur.fetchall()
    conn.close()

    return render_template('index.html', products=products, categories=categories, search=search)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        login_input = request.form.get('login')
        password = request.form.get('password')

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        if action == 'register':
            try:
                cur.execute("INSERT INTO users (login, password, role_id) VALUES (%s, %s, 2)", (login_input, password))
                conn.commit()
                flash('Регистрация успешна! Теперь войдите.', 'success')
            except mysql.connector.Error:
                flash('Ошибка: такой логин уже существует', 'danger')
        elif action == 'login':
            cur.execute("SELECT id, role_id FROM users WHERE login = %s AND password = %s", (login_input, password))
            user = cur.fetchone()
            if user:
                session['user_id'] = user['id']
                session['role_id'] = user['role_id']
                conn.close()
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль', 'danger')
        conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT o.id, p.model, oi.quantity, o.order_date
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
    """, (session['user_id'],))
    user_orders = cur.fetchall()
    conn.close()

    return render_template('orders.html', orders=user_orders)

@app.route('/buy/<int:product_id>')
def buy(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, order_date, status) VALUES (%s, NOW(), 'Оплачен')", (session['user_id'],))
    order_id = cur.lastrowid
    cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, 1)", (order_id, product_id))
    conn.commit()
    conn.close()

    flash('Товар добавлен в ваши заказы!', 'success')
    return redirect(url_for('index'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect(url_for('index'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        model = request.form.get('model')
        price = request.form.get('price')
        warranty = request.form.get('warranty')
        cat_id = request.form.get('category_id')
        man_id = request.form.get('manufacturer_id')

        cur.execute("INSERT INTO products (model, price, warranty_months, category_id, manufacturer_id) VALUES (%s, %s, %s, %s, %s)",
                    (model, price, warranty, cat_id, man_id))
        conn.commit()
        conn.close()
        flash('Товар успешно добавлен!', 'success')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    cur.execute("SELECT * FROM manufacturers")
    manufacturers = cur.fetchall()
    conn.close()

    return render_template('add_product.html', categories=categories, manufacturers=manufacturers)

if __name__ == '__main__':
    app.run(debug=True)