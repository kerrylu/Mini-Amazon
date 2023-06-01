from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, validators
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
from werkzeug.utils import secure_filename
import os
from flask import current_app as app, flash

from .models.productReview import ProductReview
from .models.sellerReview import SellerReview

from flask import Blueprint
bp = Blueprint('review', __name__)

class RecentReviewForm(FlaskForm):
    n = IntegerField('User id: ', [validators.DataRequired()])
    submit = SubmitField('Enter')

class RecentProductForm(FlaskForm):
    n = IntegerField('Product id: ', [validators.DataRequired()])
    submit = SubmitField('Enter')

class RecentSellerForm(FlaskForm):
    n = IntegerField('Seller id:', [validators.DataRequired()])
    submit = SubmitField('Enter')

@bp.route('/recent_reviews/product', methods=['GET', 'POST'])
def five_most_recent_product():
    recent = None
    form = RecentReviewForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = ProductReview.get_five_most_recent(n)
        return render_template('product_reviews.html', reviews=recent, form=form)
    return render_template('product_reviews.html', reviews=recent, form=form)

@bp.route('/recent_reviews/seller', methods=['GET', 'POST'])
def five_most_recent_seller():
    recent = None
    form = RecentReviewForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = SellerReview.get(n)
        return render_template('seller_reviews.html', reviews=recent, form=form)
    return render_template('seller_reviews.html', reviews=recent, form=form)


@bp.route('/all_product_reviews', methods=['GET', 'POST'])
def all_product_reviews():
    recent = None
    form = RecentReviewForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = ProductReview.get(n)
        return render_template('all_product_reviews.html', reviews=recent, form=form)
    return render_template('all_product_reviews.html', reviews=recent, form=form)

@bp.route('/all_seller_reviews', methods=['GET', 'POST'])
def all_seller_reviews():
    recent = None
    form = RecentReviewForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = SellerReview.get(n)
        return render_template('all_seller_reviews.html', reviews=recent, form=form)
    return render_template('all_seller_reviews.html', reviews=recent, form=form)

@bp.route('/all_product_reviews_byproduct', methods=['GET', 'POST'])
def all_product_reviews_byproduct():
    recent = None
    count = None
    average = None
    form = RecentProductForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = ProductReview.get_by_pid(n)
        count = ProductReview.count(n)
        average = ProductReview.get_average(n)
        return render_template('all_product_reviews_byproduct.html', reviews=recent, count = count, average = average, form=form)
    return render_template('all_product_reviews_byproduct.html', reviews=recent,  count = count, average = average, form=form)

@bp.route('/all_seller_reviews_byseller', methods=['GET', 'POST'])
def all_seller_reviews_byseller():
    recent = None
    count = None
    average = None
    form = RecentSellerForm()
    if form.validate_on_submit():
        n = form.n.data
        recent = SellerReview.get_by_sid(n)
        count = SellerReview.count(n)
        average = SellerReview.get_average(n)
        return render_template('all_seller_reviews_byseller.html', reviews=recent,  count = count, average = average, form=form)
    return render_template('all_seller_reviews_byseller.html', reviews=recent,  count = count, average = average, form=form)

class ProductReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')

@bp.route('/product_review/<sid>-<pid>', methods=['GET', 'POST'])
def product_review(pid, sid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = ProductReviewForm()

    if form.validate_on_submit():
        if ProductReview.add_review(current_user.id, pid, sid, form.description.data, form.rating.data ):
            return redirect(url_for('review.my_reviews'))
        elif ProductReview.add_review(current_user.id, pid, sid, form.description.data, form.rating.data) == 1:
            flash("You have already made a review for this item!")
            return redirect(url_for('users.my_reviews', uid = current_user.id))
        elif ProductReview.add_review(current_user.id, pid, sid,  form.description.data, form.rating.data) == 0:
            flash("You can only review the item after you make a purchase!")
            return redirect(url_for('index.index'))
    return render_template('product_review.html', pid = pid, form = form)

class SellerReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')


@bp.route('/seller_review/<sid>', methods=['GET', 'POST'])
def seller_review(sid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = SellerReviewForm()

    if form.validate_on_submit():
        if SellerReview.add_review(current_user.id, sid, form.description.data, form.rating.data):
            return redirect(url_for('review.my_reviews'))
        elif SellerReview.add_review(current_user.id, sid, form.description.data, form.rating.data) == 1:
            flash("You have already made a review for this item!")
            return redirect(url_for('review.my_reviews', uid = current_user.id))
        elif SellerReview.add_review(current_user.id, sid, form.description.data , form.rating.data) == 0:
            flash("You can only review the item after you make a purchase!")
            return redirect(url_for('index.index'))
    return render_template('seller_review.html', sid = sid, form = form)

@bp.route('/my_reviews', methods=['GET', 'POST'])
def my_reviews():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    previews = ProductReview.get(current_user.id)
    sreviews = SellerReview.get(current_user.id)
    return render_template('my_reviews.html', previews = previews, sreviews = sreviews)


class UpdateProductReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')


@bp.route('/my_reviews/update_product_review/<uid>-<pid>-<sid>', methods=['GET', 'POST'])
def update_product_review(uid, pid, sid):
    
    form = UpdateProductReviewForm()

    if form.validate_on_submit():
        ProductReview.update(uid, pid, sid, form.description.data, form.rating.data)
        flash("Review updated successfully!")
        
        return redirect(url_for('review.my_reviews'))
    
    return render_template('update_product_review.html', uid = uid, pid = pid, sid = sid, form = form)


@bp.route('/my_reviews/delete_product_review/<uid>-<pid>-<sid>', methods=['GET', 'POST'])
def delete_product_review(uid, pid, sid):

    d = ProductReview.delete(uid, pid, sid)
    
    return redirect(url_for('review.my_reviews'))

class UpdateSellerReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')


@bp.route('/my_reviews/update_seller_review/<uid>-<sid>', methods=['GET', 'POST'])
def update_seller_review(uid, sid):
    form = UpdateSellerReviewForm()

    if form.validate_on_submit():
        SellerReview.update(uid, sid, form.description.data, form.rating.data)
        flash("Review updated successfully!")
        
        return redirect(url_for('review.my_reviews'))

    return render_template('update_seller_review.html', uid = uid, sid = sid, form = form)

@bp.route('/my_reviews/delete_seller_review/<uid>-<sid>', methods=['GET', 'POST'])
def delete_seller_review(uid, sid):

    d = SellerReview.delete(uid, sid)
    
    return redirect(url_for('review.my_reviews'))


def allowed_image(filename):

    if not '.' in filename:
        flash("This is not an acceptable file.")
        return False
    
    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        flash("This is not the acceptable file extension.")
        return False


@bp.route('/upload-image/<uid>/<pid>', methods = ['GET', 'POST'])
def upload_form(uid, pid):

    if request.files:

        image = request.files["image"]

        if image.filename == "":
            flash("Image mush have a filename")
            return redirect(request.url)

        if not allowed_image(image.filename):
            flash("Image extension is not allowed")
            return redirect(request.url)

        else:
            filename = secure_filename(image.filename)
                
        image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
        flash("Image successfully uploaded")
        ProductReview.update_image_path(pid, uid, filename)
        return render_template('upload_file.html', uid = uid, pid = pid, filename = filename)
    else:
        filename = ProductReview.get_user_product_image_path(pid, uid)
        if filename is None:
            return render_template('upload_file.html', uid = uid, pid = pid)
        else:
            return render_template('upload_file.html', uid = uid, pid = pid, filename = filename)


@bp.route('/display-image/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename = 'img/uploads/' + filename), code = 301)


@bp.route('/ProductPage/<pid>/<uid>/show-image')
def show_image(uid, pid):
    filename = ProductReview.get_user_product_image_path(pid, uid)
    return render_template('view_image.html', pid=pid, uid=uid, filename=filename)
