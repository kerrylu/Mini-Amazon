from flask import render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_paginate import Pagination, get_page_parameter, get_page_args
from wtforms import StringField, SelectField, SubmitField, validators, RadioField
import datetime

from .models.product import Product, ProductSummary
from .models.purchase import Purchase
from .users import LoginForm

from flask import Blueprint
bp = Blueprint('index', __name__)

class IndexForm(FlaskForm):
    search = StringField([validators.DataRequired()])
    searchOption = SelectField("Search by: ", choices=["Name", "Description"])
    choiceList = [('default', 'Default Display'), ('highToLow', 'Price High to Low'), ('lowToHigh', 'Price Low to High'), ('avgRev', 'Average Review'), ('availQuant', 'Available Quantity')]
    sortBy = SelectField('Sort by: ', choices=choiceList)
    categoryList = ["All", "Clothing", "Books", "Electronics", "Home", "Outdoors", "Food"]
    categoryChoice = SelectField('Category: ', choices=categoryList)
    quantFilterList = [('all', 'Quantity'), ('greater100', '> 100'), ('50-100', '50 - 100'), ('less50', '< 50')]
    quantFilterChoice = SelectField('Filter By: ', choices=quantFilterList)
    priceFilterList = [('all', 'Price'), ('400-500', '$400 - $500'), ('300-400', '$300 - $400'), ('200-300', '$200 - $300'), ('100-200', '$100 - $200'), ('less100', '< $100')]
    priceFilterChoice = SelectField('Filter By: ', choices=priceFilterList)
    submit = SubmitField('Search')

def get_products(products, offset=0, per_page=10):
    return products[offset: offset + per_page]

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    products = ProductSummary.get_all()

    
    if form.submit.data and form.validate():
        search = form.search.data if form.search.data != None else ""
        searchBy = form.searchOption.data
        sortBy = form.sortBy.data 
        category = form.categoryChoice.data if form.categoryChoice.data != "All" else ""
        filterQuantity = form.quantFilterChoice.data
        filterPrice = form.priceFilterChoice.data
        products = ProductSummary.get_by_search(search, searchBy, sortBy, category, filterQuantity, filterPrice)

    paginated_products = get_products(products, offset=offset, per_page=20)
    pagination = Pagination(page=page, per_page=20, total=len(products))
    return render_template('index.html',
                        avail_products=paginated_products,
                        form=form,
                        pagination=pagination)