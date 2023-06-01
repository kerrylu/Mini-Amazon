import time
import datetime as DT
from flask import render_template, redirect, url_for, request
from flask_login import current_user

from .models.cart import Cart
from .models.order import Order
from .models.purchase import Purchase

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired

from flask import Blueprint
bp = Blueprint('userCart', __name__)

@bp.route('/cart', methods=['GET', 'POST'])
def cartPage():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    cart = Cart.get_all_in_cart(current_user.id)
    total_price = Cart.get_total_price(current_user.id)
    return render_template('cart.html', user_cart=cart, total_price=total_price)

@bp.route('/wishlist', methods=['GET', 'POST'])
def wishlistPage():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    cart = Cart.get_all_in_wishlist(current_user.id)
    return render_template('wishlist.html', user_cart=cart)

@bp.route('/update_quantity/<user_id>/<seller_id>/<product_id>', methods=['GET', 'POST'])
def update_quantity(user_id, seller_id, product_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    quantity = request.form['quantity']
    Cart.update_quantity(user_id, seller_id, product_id, quantity)
    return redirect(url_for('userCart.cartPage'))

@bp.route('/update_wishlist_quantity/<user_id>/<seller_id>/<product_id>', methods=['GET', 'POST'])
def update_wishlist_quantity(user_id, seller_id, product_id):
    quantity = request.form['quantity']
    Cart.update_quantity(user_id, seller_id, product_id, quantity)
    return redirect(url_for('userCart.wishlistPage'))

@bp.route('/delete_item/<user_id>/<seller_id>/<product_id>', methods=['GET', 'POST'])
def delete_item(user_id, seller_id, product_id):
    Cart.delete_item(user_id, seller_id, product_id)
    return redirect(url_for('userCart.cartPage'))

@bp.route('/add_wishlist_item_to_cart/<user_id>/<seller_id>/<product_id>', methods=['GET', 'POST'])
def add_wishlist_item_to_cart(user_id, seller_id, product_id):
    Cart.add_wishlist_item_to_cart(user_id, seller_id, product_id)
    return redirect(url_for('userCart.wishlistPage'))

@bp.route('/submit_order/<user_id>', methods=['GET', 'POST'])
def submit_order(user_id):
    order_status = Cart.check_status(user_id)
    if order_status < 0:
        return render_template('orderResult.html', status=order_status)
    else:
        user_address = Order.get_address(user_id)[0][0]
        total_price = Cart.get_total_price(user_id)
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S')
        order_id = Order.add_order(user_id, user_address, total_price, cur_time)
        ful_time = DT.datetime(2038, 1, 19, 3, 14, 7)
        all_products = Cart.get_all_in_cart(user_id)
        for product in all_products:
            Purchase.add_purchase(order_id, product.seller_id, product.product_id, product.quantity, product.price_per_unit, ful_time, user_id)
        Cart.clear_cart(user_id)       
        return render_template('orderResult.html', status=order_status)

class CartsApi(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    search = SubmitField('Search')