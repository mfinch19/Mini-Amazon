from flask import current_app as app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import exc
import datetime

# Reviews of Products
# CREATE TABLE ProductReview (
# 	user_id INT NOT NULL REFERENCES Users(id),
# 	product_id INT NOT NULL REFERENCES Products(id),
# 	date_time DATE NOT NULL,
# 	description VARCHAR(256) NOT NULL,
# 	rating DECIMAL(10, 2) NOT NULL CHECK(rating >= 1 AND rating <= 5),
# 	PRIMARY KEY (user_id, product_id)
# 	-- probably need a FOREIGN KEY
# );

class ProductReview:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.product_id = kwargs.get('product_id')
        self.date_time = kwargs.get('date_time')
        self.description = kwargs.get('description', '')
        self.rating = kwargs.get('rating')
        self.exists = kwargs.get('exists')
        self.reviews = kwargs.get('reviews')
        self.last_review = kwargs.get('last_review')
        self.avg_rating = kwargs.get('avg_rating')

    @staticmethod
    def get(user_id, offset = 0, product_id = None):
        # If no passed in `user_id`, then return all reviews for that product
        if user_id is None:
            rows = app.db.execute('''
            SELECT user_id, product_id, date_time, description, rating
            FROM ProductReview
            WHERE product_id = :product_id
            ORDER BY date_time DESC
            LIMIT 10 OFFSET :offset
            ''',
                                  product_id = product_id,
                                  offset = offset)

        # If no passed in `product_id`, then return all reviews from that user
        elif product_id is None:
            rows = app.db.execute('''
            SELECT user_id, product_id, date_time, description, rating
            FROM ProductReview
            WHERE user_id = :user_id
            ORDER BY date_time DESC
            LIMIT 10 OFFSET :offset
            ''',
                                  user_id = user_id,
                                  offset = offset)
        # If `product_id` passed in, then return review from that user for the given product
        elif product_id is not None:
            rows = app.db.execute('''
            SELECT user_id, product_id, date_time, description, rating
            FROM ProductReview
            WHERE user_id = :user_id AND product_id = :product_id
            LIMIT 10 OFFSET :offset
            ''',
                                  user_id = user_id,
                                  offset = offset,
                                  product_id = product_id)

        # If there exists a previous review, create the object
        if rows:
            reviews = [ProductReview(user_id = row[0],
                                     product_id = row[1],
                                     date_time = row[2],
                                     description = row[3],
                                     rating = row[4],
                                     exists = True) for row in rows]
            # If no product_id passed in, return just the first element, not the list
            if product_id is None or user_id is None:
                return reviews
            else:
                return reviews[0]
        # Otherwise, create an empty ProductReview object
        else:
            return(ProductReview(exists = False))

    @staticmethod
    def add_review(request, product_id):

        # Add in a check to see if the user has bought this product
        rows = app.db.execute('''
        SELECT order_id
        FROM Purchases
        WHERE buyer_id = :buyer_id AND product_id = :product_id AND status = 'Complete'
        ''',
                                      buyer_id = current_user.id,
                                      product_id = product_id)
        # This means that user has not bought from this seller
        if not rows:
            return 'you have not had a completed purchase of this product'

        # Get information to add to review
        date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        description = request.form['body']
        rating = request.form['numstars']

        try:
            rows = app.db.execute("""
            INSERT INTO ProductReview(user_id, product_id, date_time, description, rating)
            VALUES(:user_id, :product_id, :date_time, :description, :rating)
            RETURNING user_id
            """,
                                  user_id = current_user.id,
                                  product_id = product_id,
                                  date_time = date_time,
                                  description = description,
                                  rating = rating)
        # This means already a review for this product from this user
        except exc.IntegrityError as e:
            return 'you have already made a review for this seller'

        return 'Done'

    @staticmethod
    def update_review(request, product_id):
        # Get information to add to review
        date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        description = request.form['body']
        rating = request.form['numstars']

        rows = app.db.execute("""
        UPDATE ProductReview
        SET rating = :rating, description = :description, date_time = :date_time
        WHERE user_id = :user_id AND product_id = :product_id
        RETURNING user_id
        """,
                              rating = rating,
                              description = description,
                              date_time = date_time,
                              user_id = current_user.id,
                              product_id = product_id)
        return 'Done'

    @staticmethod
    def delete_review(product_id):
        rows = app.db.execute("""
        DELETE FROM ProductReview
        WHERE user_id = :user_id AND product_id = :product_id
        RETURNING user_id
        """,
                              user_id = current_user.id,
                              product_id = product_id)
        # flash('Deleted product review for product ID: ' + product_id)
        return 'Deleted product review for product ID: ' + product_id

    @staticmethod
    def get_review_stats(user_id):
        rows = app.db.execute('''
        SELECT user_id, COUNT(*) AS reviews, MAX(date_time) AS last_review, AVG(rating) AS avg_rating
        FROM ProductReview
        WHERE user_id = :user_id
        GROUP BY user_id
        ''',
                              user_id = user_id)
        # If there exists a previous review, create the object
        if rows:
            return [ProductReview(user_id = row[0],
                                  reviews = row[1],
                                  last_review = row[2],
                                  avg_rating = row[3],
                                  exists = True) for row in rows][0]
        # Otherwise, create an empty ProductReview object
        else:
            return (ProductReview(exists = False))

class ProductReviewWithName:
    def __init__(self, user_id, firstname, lastname, product_id, date_time, description, rating):
        self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.product_id = product_id
        self.date_time = date_time
        self.description = description
        self.rating = rating

    @staticmethod
    def get_reviews(product_id, offset):
        rows = app.db.execute('''
        SELECT user_id, firstname, lastname, product_id, date_time, description, rating
        FROM ProductReview, Users
        WHERE product_id = :product_id AND user_id = id
        ORDER BY date_time DESC
        LIMIT 6 OFFSET :offset
        ''',
             product_id = product_id,
             offset=offset)

        return [ProductReviewWithName(*row) for row in rows] if rows else None
