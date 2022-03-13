from flask import current_app as app

class Seller:
    def __init__(self, id, name, price, cat_name, description, image_file, available):
        self.id = id
        self.name = name
        self.cat_name = cat_name
        self.price = price
        self.description = description
        self.image_file = image_file
        self.available = available





class SellerSummary:
    def __init__(self, seller_id, firstname, lastname, products, avg_price, total_stock, reviews, avg_rating, items_sold, last_sold):
        self.seller_id = seller_id
        self.firstname = firstname
        self.lastname = lastname
        self.products = products
        self.avg_price = avg_price
        self.total_stock = total_stock
        self.reviews = reviews
        self.avg_rating = avg_rating
        self.items_sold = items_sold
        self.last_sold = last_sold

    @staticmethod
    def get(seller_id):
        rows = app.db.execute('''
        SELECT *
        FROM SellerSummary
        WHERE seller_id = :seller_id
        ''',
             seller_id=seller_id)

        return [SellerSummary(*row) for row in rows] if rows else None
