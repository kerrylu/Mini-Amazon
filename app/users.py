from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms import StringField, SelectField, SubmitField, validators

from .models.user import User
from .models.purchase import Purchase
from .models.order import Order

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

    


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

class UsersApi(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    search = SubmitField('Search')

@bp.route('/api/users', methods=['GET', 'POST'])
def get_users_purchases():
    form = UsersApi()
    data=User.get_purchases(form.user_id.data)
    if data: 
        return render_template('users_api.html', title='User API', form=form, data = data)
    return render_template('users_api.html', title='User API', form=form)

class SortPurchases(FlaskForm):
    choiceList = [('lastToFirst', 'Date Fulfilled: Last to First'),('firstToLast', 'Date Fulfilled: First to Last'), ('highToLow', 'Total Amount: High to Low'), ('lowToHigh', 'Total Amount: Low to High'), ('prid', 'Order ID')]
    sortBy = SelectField('Sort by:', choices=choiceList)
    submit = SubmitField('Sort')

    # form = SearchIndexForm()
    # selectForm = SelectIndexForm()
    # products = Product.get_all()
    # if not current_user.is_authenticated:
    #     return redirect(url_for('users.login'))
    # if form.submit.data and form.validate():
    #     name = form.name.data
    #     products = Product.search_by_name(name)
    # if selectForm.submit.data and selectForm.validate():
    #     products = Product.get_all()
    #     sortSelection = selectForm.sortBy.data
    #     if sortSelection == 'pid':
    #         products = Product.get_all()
    #     elif sortSelection == 'highToLow':
    #         products = Product.sort_high_to_low()
    #     elif sortSelection == 'lowToHigh':
    #         products = Product.sort_low_to_high()
    # return render_template('index.html',
    #                     avail_products=products,
    #                     form=form,
    #                     selectForm=selectForm)

@bp.route('/purchases', methods=['GET', 'POST'])
def get_active_user_purchases():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    sortForm = SortPurchases()
    data=User.sort_purchases_date_desc(current_user.id)

    if sortForm.submit.data and sortForm.validate():
        sortSelection = sortForm.sortBy.data
        if sortSelection == 'lastToFirst':
            data = User.sort_purchases_date_desc(current_user.id)
        elif sortSelection == 'firstToLast':
            data = User.sort_purchases_date_asc(current_user.id)
        elif sortSelection == 'highToLow':
            data = User.sort_purchases_price_desc(current_user.id)
        elif sortSelection == 'lowToHigh':
            data = User.sort_purchases_price_asc(current_user.id)
        elif sortSelection == 'prid':
            data = User.sort_purchases_id(current_user.id)
    # if data: 
    #     return render_template('users_api.html', title='User API', form=form, data = data)
    return render_template('purchases.html', title='User API', data = data, sortForm = sortForm)


class UpdatePwd(FlaskForm):
    newPWD = PasswordField('Password', validators=[DataRequired()])
    confPWD = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Submit')

@bp.route('/account', methods=['GET', 'POST'])
def get_user_info():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    data = User.get_accountinfo(current_user.id)
    reviews = User.get_seller_reviews(current_user.id)
    isSeller=User.isSeller(current_user.id)
    pwdForm = UpdatePwd()

    if pwdForm.submit.data:
        if pwdForm.newPWD.data and pwdForm.newPWD.data == pwdForm.confPWD.data:
            User.update_user_pwd(current_user.id, pwdForm.newPWD.data)
        

    # print(data)
    
    if request.method == 'POST' and not pwdForm.submit.data:
        if request.form:
            email = request.form['email'] if request.form['email'] else data[0][1]
            first = request.form['first'] if request.form['first'] else data[0][2]
            last = request.form['last'] if request.form['last'] else data[0][3]
            location = request.form['location'] if request.form['location'] else data[0][4]
            balance = float(request.form['balance']) if float(request.form['balance']) and float(request.form['balance'])>0  else data[0][5]
            User.update_accountinfo(current_user.id, email, first, last, location, balance)
        else:
            User.newSeller(current_user.id)
        return redirect(url_for('index.index'))
    # if data: 
    #     return render_template('users_api.html', title='User API', form=form, data = data)
    return render_template('account_info.html', title='User API', data = data, reviews = reviews, pwdForm = pwdForm, isSeller= isSeller)

@bp.route('/order_detail/<id>', methods=['GET', 'POST'])
def order_detail(id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    order = Purchase.get(id)
    order_fulfilled_status = Order.get_status(id)[0][0]
    return render_template('detailed_order.html', order=order, status=order_fulfilled_status)

@bp.route('/users_details', methods=['GET', 'POST'])
def all_users_details():
    data = User.get_all()
    return render_template('all_users_details.html', data = data)

@bp.route('/users_details/<id>', methods=['GET', 'POST'])
def user_details(id):
    data = User.get_accountinfo(id)
    reviews = User.get_seller_reviews(id)
    isSeller=User.isSeller(id)
    return render_template('user_details.html', data=data, reviews=reviews, isSeller=isSeller)

