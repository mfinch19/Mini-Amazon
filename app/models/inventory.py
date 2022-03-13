from flask import current_app as app
from flask_login import current_user


class Inventory:
    # def __init__(self, id, name, price, cat_name, description, image_file, available):
    #     self.id = id
    #     self.name = name
    #     self.cat_name = cat_name
    #     self.price = price
    #     self.description = description
    #     self.image_file = image_file
    #     self.available = available

    def __init__(self, seller_id, product_id, price, prod_name, stock, firstname, lastname):
            self.seller_id = seller_id
            self.product_id = product_id
            self.price = price
            self.prod_name = prod_name
            self.stock = stock
            self.firstname = firstname
            self.lastname = lastname

        

    # def __repr__():
    #     return ""

    @staticmethod
    def get(seller_id):
        rows = app.db.execute('''
        SELECT seller_id, product_id, price, stock
            FROM SellsItem
            WHERE seller_id = :seller_id
        ''',
        seller_id=seller_id)
        return Inventory(*(rows[0])) if rows is not None else None

    @staticmethod
    def getProduct(product_id):
        rows = app.db.execute('''
        SELECT stock, price
        FROM SellsItem 
        WHERE seller_id=:seller_id AND product_id = :product_id
        ''',
        product_id=product_id,
        seller_id=current_user.id)
        return rows[0]



    @staticmethod
    def get_all(available, seller_id, offset=0):
        if seller_id is None:
            print(seller_id)
            rows = app.db.execute('''
            SELECT si.seller_id, si.product_id, si.price, p.name, si.stock, u.firstname, u.lastname
            FROM SellsItem si, Products p, Users u
            WHERE si.product_id = p.id AND u.id = si.seller_id
            ORDER BY si.seller_id
            LIMIT 10 OFFSET :offest
            '''.format(available),
            available=available, offset=offset)
            return [Inventory(*row) for row in rows]
        else:
            print(seller_id)
            rows = app.db.execute('''
            SELECT s.seller_id, s.product_id, s.price, p.name, s.stock, u.firstname, u.lastname
            FROM SellsItem s, Products p, Users u
            WHERE s.seller_id = :seller_id AND s.product_id = p.id AND u.id = s.seller_id
            LIMIT 10 OFFSET :offset
            ''',
<<<<<<< HEAD
            available=available,
            seller_id=seller_id)
=======
            seller_id=seller_id, offset=offset)
>>>>>>> fd4f25f744e800425f6c85729aac8763b507871d
            return [Inventory(*row) for row in rows]
    
    @staticmethod
    def countItems(seller_id) : 
        c = app.db.execute('''
        SELECT COUNT(seller_id)
        FROM SellsItem s
        WHERE s.seller_id= :seller_id
        ''',
        seller_id=seller_id) 
        return c[0][0]



    @staticmethod
    def productList(id):
        rows = app.db.execute('''
        SELECT s.product_id, s.price, s.stock, s.seller_id, u.firstname, u.lastname
        FROM SellsItem s, Users u
        WHERE s.product_id = :id AND s.seller_id = u.id
        ''',
        id=id)
        return [Inventory(*row) for row in rows] if rows is not None else 'No current sellers'


