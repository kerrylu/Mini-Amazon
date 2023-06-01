from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, validators
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import DetailedInventory
from .models.cart import Cart
from .models.review import Review, ProductReview

from flask import Blueprint
bp = Blueprint('products', __name__)

class MostExpensiveForm(FlaskForm):
    k = IntegerField('Display this many of the top most expensive products:', [validators.DataRequired()])
    submit = SubmitField('Enter')

@bp.route('/most_expensive', methods=['GET', 'POST'])
def most_expensive():
    mostExp = None
    form = MostExpensiveForm()
    if form.validate_on_submit():
        k = form.k.data
        mostExp = Product.most_expensive(k)
        return render_template('most_expensive.html', mostExp=mostExp, form=form)
    return render_template('most_expensive.html', mostExp=mostExp, form=form)

@bp.route('/product_details/<id>', methods=['GET', 'POST'])
def product_details(id):
    product = Product.get(id)
    sellers = DetailedInventory.get_by_pid(id)
    reviews = ProductReview.get_by_pid(id)
    return render_template('product_details.html', product=product, sellers=sellers, reviews=reviews)

@bp.route('/add_to_cart/<seller_id>/<product_id>/<price>', methods=['GET', 'POST'])
def add_to_cart(seller_id, product_id, price):
    quantity = request.form['quantity']
    user_id = current_user.id
    Cart.add_to_cart(user_id, seller_id, product_id, quantity, price)
    return redirect(url_for('products.product_details', id = product_id))

@bp.route('/add_to_wishlist/<seller_id>/<product_id>/<price>', methods=['GET', 'POST'])
def add_to_wishlist(seller_id, product_id, price):
    quantity = request.form['quantity']
    user_id = current_user.id
    Cart.add_to_wishlist(user_id, seller_id, product_id, quantity, price)
    return redirect(url_for('products.product_details', id = product_id))

@bp.route('/upvote_review/<user_id>/<product_id>/<seller_id>', methods=['GET', 'POST'])
def upvote_review(user_id, product_id, seller_id):
    Review.upvote(user_id, product_id, seller_id)
    return redirect(url_for('products.product_details', id = product_id))