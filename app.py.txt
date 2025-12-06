from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'

# Dummy data for products
products = [
    {"id": 1, "name": "Classic White T-Shirt", "price": 499, "image": "https://placehold.co/300?text=White+T-Shirt", "description": "High quality cotton t-shirt."},
    {"id": 2, "name": "Blue Denim Jeans", "price": 1299, "image": "https://placehold.co/300?text=Blue+Jeans", "description": "Comfortable fit denim jeans."},
    {"id": 3, "name": "Black Hoodie", "price": 999, "image": "https://placehold.co/300?text=Black+Hoodie", "description": "Warm and stylish hoodie."},
    {"id": 4, "name": "Summer Dress", "price": 899, "image": "https://placehold.co/300?text=Summer+Dress", "description": "Floral print summer dress."}
]

def get_product_by_id(product_id):
    for product in products:
        if product['id'] == product_id:
            return product
    return None

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product:
        return render_template('product.html', product=product)
    return "Product not found", 404

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total_price)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    if request.method == 'POST':
        # Here you would integrate with a payment gateway (e.g., Stripe, PayPal, Razorpay)
        # For this demo, we'll just clear the cart and show a success message.
        
        # Log the order details (for the shop owner to see)
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        print(f"New Order Received!\nName: {name}\nAddress: {address}\nPhone: {phone}\nTotal: ₹{total_price}")
        
        session.pop('cart', None)
        return render_template('checkout.html', success=True)
    return render_template('checkout.html', cart=cart, total=total_price)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    # Remove the first occurrence of the product
    for item in cart:
        if item['id'] == product_id:
            cart.remove(item)
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
