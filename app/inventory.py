from flask import render_template, redirect, url_for, flash, request
import time
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, DecimalField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from decimal import ROUND_HALF_UP
from flask_paginate import Pagination, get_page_parameter, get_page_args
import os

from .models.inventory import Inventory
from .models.inventory import OrderInfo
from .models.inventory import LineItem
from .models.order import Order
from .models.user import User

from flask import Blueprint
bp = Blueprint('inventory', __name__)

class SellerForm(FlaskForm):
    seller = IntegerField('SellerID', validators=[DataRequired()])
    submit = SubmitField('Enter')

@bp.route('/inventory', methods=['GET','POST'])
def get_products():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    sid = None
    products = None
    form = SellerForm()
    if form.validate_on_submit():
        sid = Inventory.auth_sid(form.seller.data)
        if sid is None:
            return redirect(url_for('inventory.get_products'))
        sid = form.seller.data
        products = Inventory.get_by_sid(form.seller.data)
        return render_template('inventory.html', form = form, sid = sid, products=products)
    return render_template('inventory.html', form = form, sid = sid, products = products)

class AddNewProductForm(FlaskForm):
    prodName = StringField('Product Name', validators=[DataRequired()])
    catList = ["Clothing", "Books", "Electronics", "Home", "Outdoors", "Food"]
    prodCat = SelectField('Product Category', choices=catList)
    prodDesc = StringField('Product Description', validators=[DataRequired()])
    prodPrice = DecimalField('Price',places=2, rounding=ROUND_HALF_UP, validators=[DataRequired()])
    image = StringField('Image',validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Enter')

class AddProductForm(FlaskForm):
    productID = IntegerField('Product ID',validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Enter')

class EditProductForm(FlaskForm):
    productID = IntegerField('Product ID',validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Enter')

class RemoveProductForm(FlaskForm):
    productID = IntegerField('Product ID',validators=[DataRequired()])
    submit = SubmitField('Enter')

@bp.route('/edit_inventory', methods=['GET','POST'])
def edit_inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    curID = current_user.get_id()
    ret = Inventory.auth_sid(curID)
    if ret is None:
        return redirect(url_for('index.index'))
    products = Inventory.get_by_sid(curID)
    pag_products = products[offset:offset+per_page]
    pagination = Pagination(page=page, per_page=10, total=len(products))
    return render_template('edit_inventory.html', sid=curID, products=pag_products, pagination=pagination)

@bp.route('/edit_inventory/add_new_product', methods=['GET','POST'])
def add_new_product():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    form = AddNewProductForm()
    curID = current_user.get_id()
    products = None
    if form.validate_on_submit():
        name = form.prodName.data
        category = form.prodCat.data
        descrip = form.prodDesc.data
        price = form.prodPrice.data
        image = form.image.data
        quantity = form.quantity.data
        ret = Inventory.auth_add_new_product(name)
        if ret is not None:
            return redirect(url_for('inventory.edit_inventory'))
        Inventory.addNewProduct(name,category,descrip,price,image,curID,quantity)
        products = Inventory.get_by_sid(curID)
        pag_products = products[offset:offset+per_page]
        pagination = Pagination(page=page, per_page=10, total=len(products))
        return redirect(url_for('inventory.edit_inventory'))
    return render_template('add_new_product.html', form=form, sid = curID, products=products)

@bp.route('/edit_inventory/add_product', methods=['GET','POST'])
def add_product():
    form = AddProductForm()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    curID = current_user.get_id()
    products = None
    if form.validate_on_submit():
        productID = form.productID.data
        quantity = form.quantity.data
        ret = Inventory.auth_add_product(curID,productID)
        if ret is None:
            return redirect(url_for('inventory.edit_inventory'))
        Inventory.addProduct(productID,curID,quantity)
        products = Inventory.get_by_sid(curID)
        pag_products = products[offset:offset+per_page]
        pagination = Pagination(page=page, per_page=10, total=len(products))
        return redirect(url_for('inventory.edit_inventory'))
    return render_template('add_product.html', form=form, sid = curID, products=products)

@bp.route('/edit_inventory/edit_product', methods=['GET','POST'])
def edit_product():
    form = EditProductForm()
    curID = current_user.get_id()
    products = None
    if form.validate_on_submit():
        productID = form.productID.data
        quantity = form.quantity.data
        ret = Inventory.auth_edit_product(productID,curID)
        if ret is None:
            return redirect(url_for('inventory.edit_inventory'))
        Inventory.editProduct(productID,curID,quantity)
        products = Inventory.get_by_sid(curID)
        return render_template('edit_product.html', form=form, sid = curID, products=products)
    return render_template('edit_product.html', form=form, sid = curID, products=products)

@bp.route('/edit_inventory/remove_product', methods=['GET','POST'])
def remove_product():
    form = RemoveProductForm()
    curID = current_user.get_id()
    products = None
    if form.validate_on_submit():
        productID = form.productID.data
        ret = Inventory.auth_edit_product(productID,curID)
        if ret is None:
            return redirect(url_for('inventory.edit_inventory'))
        Inventory.removeProduct(productID,curID)
        products = Inventory.get_by_sid(curID)
        return render_template('remove_product.html', form=form, sid = curID, products=products)
    return render_template('remove_product.html', form=form, sid = curID, products=products)

@bp.route('/update_inventory_quantity/<seller_id>/<product_id>', methods=['GET', 'POST'])
def update_inventory_quantity(seller_id, product_id):
    quantity = request.form['quantity']
    Inventory.update_inventory_quantity(seller_id, product_id, quantity)
    return redirect(url_for('inventory.edit_inventory'))

@bp.route('/delete_inventory_item/<seller_id>/<product_id>', methods=['GET', 'POST'])
def delete_inventory_item(seller_id, product_id):
    Inventory.delete_inventory_item(seller_id, product_id)
    return redirect(url_for('inventory.edit_inventory'))

@bp.route('/order_fulfillment/', methods=['GET','POST'])
def order_fulfillment():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    curID = current_user.get_id()
    ret = Inventory.auth_sid(curID)
    if ret is None:
        return redirect(url_for('index.index'))
    orderInfo = OrderInfo.get_orders(curID)
    pag_orders = orderInfo[offset:offset+per_page]
    pagination = Pagination(page=page, per_page=10, total=len(orderInfo))
    return render_template('orders_info.html', sid=curID, orders=pag_orders, pagination=pagination)

@bp.route('/order_fulfill/<order_id>',methods=['GET','POST'])
def order_fulfill(order_id):
    curID = current_user.get_id()
    uid = Order.get_user(order_id)
    userInfo = User.get(uid)
    lineItems = LineItem.get_order(curID,order_id)
    return render_template('order_fulfill.html', order_id=order_id, userInfo=userInfo,lineItems = lineItems)

@bp.route('/order_fulfill/<order_id>/<product_id>',methods=['GET','POST'])
def fulfill_item(order_id, product_id):
    curID = current_user.get_id()
    done = LineItem.fulfill_item(order_id, product_id,time.strftime('%Y-%m-%d %H:%M:%S'))
    if done is not None:
        Order.fulfill_order(order_id,time.strftime('%Y-%m-%d %H:%M:%S'))
    return redirect(url_for('inventory.order_fulfill',order_id=order_id))