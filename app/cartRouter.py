from flask import flash, redirect, render_template, request, url_for, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.product import ProductSummary
from .models.product_sellers import SellerSummary
from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.seller_review import SellerReview
from .models.product_review import ProductReview
from .models.product_review import ProductReviewWithName
from .models.cart import cart


from flask import Blueprint
bp = Blueprint('cartRouter', __name__)

# cart_update html
@bp.route('/cart_update/<uid>/<sid>/<pid>/<quan>/<price>', methods = ['POST', 'GET'])
def cart_update(uid, sid, pid, quan, price):

    return render_template('cart_update.html',
                           user_id = uid,
                           seller_id = sid,
                           product_id = pid,
                           quantity = quan,
                           price_per_item = price)


# connects to backend for delete_cart_element
@bp.route('/delete_cart_element/<user_id>/<seller_id>/<product_id>/', methods = ['POST', 'GET'])
def delete_cart_element(user_id, seller_id, product_id):
    cart.remove_product_in_cart(user_id = user_id, seller_id = seller_id, product_id = product_id)

    return redirect(url_for('index.cart_page'))

# connects to backend for update_cart_quantity
@bp.route('/update_cart_quantity/<user_id>/<seller_id>/<product_id>/', methods = ['POST', 'GET'])
def update_cart_quantity(user_id, seller_id, product_id):
    quantity = request.form['quantity']
    cart.update_cart(user_id = user_id, seller_id = seller_id, product_id = product_id, quantity = quantity)

    return redirect(url_for('index.cart_page'))

# connects to backend for update_cart_quantity
@bp.route('/purchase_from_cart/<user_id>/', methods = ['POST', 'GET'])
def purchase_from_cart(user_id):
    order_status = cart.check_order(user_id = user_id)
    print('tracking order satus:')
    print( order_status)
    # order is successful
    if order_status == 0:  
        cart.make_cart_order(user_id = user_id)
        return redirect(url_for('cartRouter.order_result_page', type= 'sucess'))
    # not enough balance
    if order_status == 1:
        render_template('order_result.html',
                           type = 'balance')
        return redirect(url_for('cartRouter.order_result_page', type= 'balance'))
    # not enough stock
    if order_status == 2:
        return redirect(url_for('cartRouter.order_result_page', type= 'stock'))


@bp.route('/order_result_page/<type>', methods = ['POST', 'GET'])
def order_result_page(type):

    return render_template('order_result.html',
                           type = type)


# connects to backend for add_to_cart
@bp.route('/add_cart/<user_id>/<seller_id>/<product_id>/<quantity>/', methods = ['POST', 'GET'])
def add_cart(user_id, seller_id, product_id, quantity):
    quantity = request.form['quantity']
    cart.add_item_to_cart(user_id = user_id, seller_id = seller_id, product_id = product_id, quantity = quantity)
    return redirect(url_for('index.cart_page'))


# connects to backend for save_for_later
@bp.route('/save_for_later/<user_id>/<seller_id>/<product_id>/', methods = ['POST', 'GET'])
def save_for_later(user_id, seller_id, product_id):
    quantity = 0
    cart.update_cart(user_id = user_id, seller_id = seller_id, product_id = product_id, quantity = quantity)

    return redirect(url_for('index.cart_page'))

# connects to backend for apply_promo_product
@bp.route('/apply_promo_product/<user_id>/<seller_id>/<product_id>/', methods = ['POST', 'GET'])
def apply_promo_product(user_id, seller_id, product_id):
    code = request.form['code']
    cart.apply_promo(code = code, user_id = user_id, seller_id = seller_id, product_id = product_id)
    return redirect(url_for('index.cart_page'))


# connects to backend for apply_promo_cart
@bp.route('/apply_promo_cart/<user_id>/', methods = ['POST', 'GET'])
def apply_promo_cart(user_id):
    code = request.form['code']
    cart.apply_promo_cart(code = code, user_id = user_id)
    return redirect(url_for('index.cart_page'))
