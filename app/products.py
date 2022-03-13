from flask import redirect, render_template, request
from flask_login import current_user
import statistics
import datetime

from .models.product import Product
from .models.product import ProductSummary
from .models.product import ProductSellers
from .models.purchase import Purchase
from .models.seller_review import SellerReview
from .models.product_review import ProductReview
from .models.product_review import ProductReviewWithName
from .models.inventory import Inventory
from .models.categories import Category
from .reviews import format_value




from flask import Blueprint
bp = Blueprint('products', __name__)

def get_avg(reviews):
    avg_rating = 0
    if reviews:
        for x in reviews:
            avg_rating+=x.rating
        avg_rating = avg_rating / len(reviews)
    return avg_rating


@bp.route('/productPage/<id>/<page>', methods = ['POST', 'GET'])
def productPage(id,page=0):
    page = int(page)
    offset = page * 6
    product = Product.get(id)
    summary = ProductSummary.get(product_id=id)[0]
    summary.avg_price = format_value(summary.avg_price, type = 'avg_price')
    summary.avg_rating = format_value(summary.avg_rating, type = 'avg_rating')
    sellers = ProductSellers.productSellers(id=id)
    for seller in sellers:
        seller.price = format_value(seller.price, type = "avg_price")
    if request.form:
        sort_by = request.form.get("sort_type")
        direction = request.form.get("direction")
        if sort_by == 'stock' and direction == 'asc':
            sellers = sorted(sellers, key=lambda x: x.stock)
        elif sort_by == 'stock' and direction == 'desc':
            sellers = sorted(sellers, key=lambda x: x.stock, reverse=True)
        elif sort_by == 'price' and direction == 'asc':
            sellers = sorted(sellers, key=lambda x: x.price)
        elif sort_by == 'price' and direction == 'desc':
            sellers = sorted(sellers, key=lambda x: x.price, reverse=True)
        
        
        

        


    reviews = ProductReviewWithName.get_reviews(product_id=id, offset=offset)
    stop = False
    if not(reviews):
        stop = True
    
    return render_template('productPage.html',
                           product=product,
                           summary=summary,
                           stop=stop,
                            sellers=sellers,
                            reviews=reviews,
                            page=page
    
                            )

@bp.route('/seller_product/<id>', methods = ['POST', 'GET'])
def seller_product(id):
    product = Product.get(id)
    sellers = ProductSellers.productSellers(id=id)
    reviews = ProductReviewWithName.get_reviews(product_id=id)
    avg_rating = get_avg(reviews)
    seller_id = current_user.id
    return render_template('seller_product.html',
                           product=product,
                            sellers=sellers,
                            reviews=reviews,
                            avg_rating=avg_rating,
                            seller_id=seller_id
                            )

@bp.route('/add_product/<id>', methods = ['POST', 'GET'])
def add_product(id):
    # get all available products for sale:
    product = Product.get(id)
    seller_id = current_user.id
    mode = "add"
    # check if we already sell this item 


    if ProductSellers.alreadySells(id): 
        products = Product.get_first_ten(available=True)
        return render_template('create_product.html',
                           products=products,
                           message="You already sell this item!")
    else: 
        return render_template('add_product_page.html',
                           product=product,
                           seller=seller_id,
                           mode=mode)

@bp.route('/edit_product/<id>', methods = ['POST', 'GET'])
def edit_product(id):
    # get all available products for sale:
    product = Product.get(id)
    seller_id = current_user.id
    mode="edit"
    seller_product = Inventory.getProduct(id)

    return render_template('add_product_page.html',
                           product=product,
                           seller_product=seller_product,
                           seller=seller_id,
                           editing=True,
                           mode=mode)




@bp.route('/write_product/<id>/<mode>', methods = ['POST', 'GET'])
def write_product(id, mode):
    # get all available products for sale:
    # product = Product.get(id)

    # If valid inputs, call product.write_product 
    if mode == "add":
        message = ProductSellers.addProduct(id=id, request=request)
    else: 
        message = ProductSellers.editProduct(id=id, request=request)
    
    product=Product.get(id)

    # else prompt the user again 
    inventory = Inventory.get_all(available=True, seller_id=current_user.id)
    if message == False:
        return render_template('add_product_page.html',
                           product=product,
                           seller=current_user.id,
                           mode=mode,
                           error=True)

    product=Product.get(id)

    if mode == "add":
        return render_template('inventory.html',
                           sold_products=inventory,
                           message=message + product.name + " to your inventory", 
                           page=0)
    else: 
        message = ProductSellers.editProduct(id=id, request=request)
        return render_template('inventory.html',
                           sold_products=inventory,
                           message=message + product.name,
                           page=0)
                        #    Need to have this go to seller_product page once it's added to the DB 

@bp.route('/delete_product/<id>', methods = ['POST', 'GET'])
def delete_product(id):
    # get all available products for sale:
    # product = Product.get(id)

    # If valid inputs, call product.write_product 

    # added = ProductSellers.addProduct(id=id, request=request)
    product=Product.get(id)
    # else prompt the user again 
    message = ProductSellers.deleteProduct(id=id)

    inventory = Inventory.get_all(available=True, seller_id=current_user.id)



    return render_template('inventory.html',
                           sold_products=inventory,
                           message=message+product.name + " from your inventory", page=0)


@bp.route('/products_by_cat/<cat_name>/<page>/<amount>/<sort_by>/<direction>/<search>', methods = ['POST', 'GET'])
def products_by_cat(cat_name, page = 0, amount = 10, sort_by = 'none', direction='none', search='...'):
    categories = Category.get_all()
    amounts = [10,15,25,50]
    amount = int(amount)
    page = int(page)
    offset = page * amount
    if request.form:
        if request.form.get("sort_type"):
            sort_by = request.form.get("sort_type")
        if request.form.get("direction"):
            direction = request.form.get("direction")
        if request.form.get("term"):
            search = request.form.get("term")
    

    products = ProductSummary.get_summaries_by_cat(cat_name=cat_name, amount=amount, offset=offset, sort_by=sort_by, direction=direction, search=search)
    if products: 
        for product in products:
            product.avg_price = format_value(product.avg_price, type = 'avg_price')
            product.avg_rating = format_value(product.avg_rating, type = 'avg_rating')
    # find the products current user has bought:
    return render_template('products_by_cat.html',
                            direction=direction,
                            search_term=search,
                            sort_by=sort_by,
                            cat_name=cat_name,
                           products=products,
                           amounts=amounts,
                           chosen_amount=amount,
                           categories = categories,
                           page=page)


@bp.route('/create_new_product/', methods = ['POST', 'GET'])
def create_new_product():
    categories = Category.get_all()
    return render_template('new_product.html',
                           categories = categories)

@bp.route('/add_new_product/', methods = ['POST', 'GET'])
def add_new_product():
    num_products = len(Product.get_all(available=False))
    products = Product.get_all(available=False)
    ids = [x.id for x in products]
    new_id=num_products+1
    while new_id in ids:
        new_id+=1
    Product.add_new_product(request=request, new_id=new_id)
    return write_product(new_id,'add')
    # ProductSellers.addProduct(id=new_id, request=request)

@bp.route('/most_popular/', methods = ['POST', 'GET'])
def most_popular():
    products = ProductSummary.most_popular()
    for product in products:
            product.avg_price = format_value(product.avg_price, type = 'avg_price')
            product.avg_rating = format_value(product.avg_rating, type = 'avg_rating')
    return render_template('most_popular.html',
                           products=products)










