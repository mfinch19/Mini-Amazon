from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
import statistics
import datetime

from .models.product import Product
from .models.product import ProductSummary
from .models.product import ProductSellers
from .models.purchase import Purchase
from .models.product_sellers import SellerSummary
from .models.seller_review import SellerReview
from .models.product_review import ProductReview
from .models.product_review import ProductReviewWithName

from flask import Blueprint
bp = Blueprint('reviews', __name__)

# Format NoneType values correctly
def format_value(value, type):

    if value is None:
        if type == 'avg_price':
            value = 'No current listings'
        else:
            value = 'No reviews'
    else:
        if type == 'avg_price':
            value = '$' + str(round(value, 2))
        else:
            value = str(round(value, 2))

    return value

# Get information related to specified user and product/seller
def get_info(object_id, type):
    # Get information related to specified user and product
    if type == 'products':
        # Get previous user review for the product
        prev_review = ProductReview.get(user_id = current_user.id,
                                        product_id = object_id)
        # Get product summary
        summary = ProductSummary.get(product_id = object_id)[0]

    # Get information related to specified user and seller
    else:
        # Get previous user review for the seller
        prev_review = SellerReview.get(user_id = current_user.id,
                                       seller_id = object_id)
        # Get seller summary
        summary = SellerSummary.get(seller_id = object_id)[0]
        summary.name = summary.firstname + ' ' + summary.lastname # Make seller name as first last

    summary.avg_price = format_value(summary.avg_price, type = 'avg_price')
    summary.avg_rating = format_value(summary.avg_rating, type = 'avg_rating')

    info = {
    "prev_review": prev_review,
    "summary": summary
    }
    return info

# Front-end submitting review
# object_id one of product_id/seller_id, type one of 'products' or 'sellers'
@bp.route('/write_review/<object_id>/<type>', methods = ['POST', 'GET'])
def write_review(object_id, type):
    # Get product/seller information for product/seller review
    info = get_info(object_id = object_id, type = type)

    return render_template('submit_review.html',
                           object_id = object_id,
                           type = type, # Either 'products' or 'sellers'
                           prev_review = info.get('prev_review'),
                           summary = info.get('summary'),
                           review_submitted = False)

# Backend for submitting review
# object_id one of product_id/seller_id, type one of 'products'/'sellers', update one of 'True'/'False'
@bp.route('/add_review/<object_id>/<type>/<update>', methods = ['POST', 'GET'])
def add_review(object_id, type, update):
    # If adding new review (update = False)
    if update == 'False':
        # If adding a product review
        if type == 'products':
            result = ProductReview.add_review(request = request,
                                              product_id = object_id)
        # If adding a seller review
        else:
            result = SellerReview.add_review(request = request,
                                             seller_id = object_id)
    # If editing/updating review
    else:
        # If updating a product review
        if type == 'products':
            result = ProductReview.update_review(request = request,
                                                 product_id = object_id)
        # If updating a seller review
        else:
            result = SellerReview.update_review(request = request,
                                                seller_id = object_id)

    # Get information related to specific product/seller
    info = get_info(object_id = object_id, type = type)

    return render_template('submit_review.html',
                           object_id = object_id,
                           type = type,
                           prev_review = info.get('prev_review'),
                           summary = info.get('summary'),
                           review_submitted = True,
                           result = result)

# Backend for deleting review
# object_id one of product_id/seller_id, type one of 'products'/'sellers'
@bp.route('/delete_review/<type>/<object_id>/', methods = ['POST', 'GET'])
def delete_review(type, object_id):
    page = request.args.get('page')
    if type == 'products':
        # Delete the product review
        result = ProductReview.delete_review(product_id = object_id)
    else:
        # Delete the seller review
        result = SellerReview.delete_review(seller_id = object_id)
    # print(result)
    return redirect(url_for('index.review_history',
                            type = type,
                            page = page))
