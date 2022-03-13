from flask import current_app as app
from faker import Faker
from datetime import datetime


'''
--- Carts Guru
-- Cart
CREATE TABLE Cart (
	user_id INT NOT NULL REFERENCES Users(id),
	seller_id INT NOT NULL REFERENCES Users(id),
	product_id INT NOT NULL REFERENCES Products(id),
	quantity INT NOT NULL CHECK(quantity >= 0),
	price_per_item DECIMAL(10, 2) NOT NULL CHECK(price_per_item >= 0),
	PRIMARY KEY(user_id, seller_id, product_id)
);
'''

class cart:
    def __init__(self, user_id, seller_id, product_id, quantity, price_per_item):
        self.user_id = user_id
        self.seller_id = seller_id
        self.product_id = product_id
        self.quantity = quantity
        self.price_per_item = price_per_item
    
    @staticmethod
    # method to get current quantity of prdoucts in cart
    def get_current_quantity(user_id):
        rows = app.db.execute('''
            SELECT COUNT(DISTINCT product_id)
            FROM Cart
            WHERE user_id = :user_id
            ''',
                              user_id = user_id)
        return rows[0][0] if rows else None
    
    @staticmethod
    # method to get the exact line in the cart 
    def get(user_id, seller_id, product_id):
        rows = app.db.execute('''
            SELECT user_id, seller_id, product_id, quantity, price_per_item
            FROM Cart
            WHERE user_id = :user_id, seller_id = seller_id, product_id = product_id
            ''',
                              user_id = user_id, seller_id = seller_id, product_id = product_id)
        return cart(*(rows[0])) if rows else None   

    @staticmethod
    # get all cart input of a user
    def get_all_cart_input(user_id):
        rows = app.db.execute('''
            SELECT *
            FROM Cart
            WHERE user_id = :user_id AND quantity > 0
            ORDER BY seller_id 
            ''',
                              user_id = user_id)
        return [cart(*row) for row in rows]

    @staticmethod
    # get all cart input of a user
    def get_save_cart(user_id):
        rows = app.db.execute('''
            SELECT *
            FROM Cart
            WHERE user_id = :user_id AND quantity = 0
            ORDER BY seller_id 
            ''',
                              user_id = user_id)
        return [cart(*row) for row in rows]

    
    @staticmethod
    # method to calculate the total price of products in the cart 
    def get_total_price(user_id):
        total = 0
        cart_content = cart.get_all_cart_input(user_id)
        
        for c in cart_content:
            total += c.price_per_item*c.quantity
        
        return total

    @staticmethod
    # backend method to add product to cart of a user
    def add_item_to_cart(user_id, seller_id, product_id, quantity):
        price_per_item = cart.get_product_price(product_id, seller_id)
        app.db.execute('''
            INSERT INTO Cart(user_id, seller_id, product_id, quantity, price_per_item)
            VALUES(:user_id, :seller_id, :product_id, :quantity, :price_per_item)
            RETURNING user_id
            ''',
                              user_id = user_id, seller_id = seller_id, product_id = product_id, quantity=quantity, price_per_item=price_per_item)



    @staticmethod
    # backend method to update quantity of product in cart
    def update_cart(user_id, seller_id, product_id, quantity): 
        #quantity = int(request.form['quantity'])
        app.db.execute('''
        UPDATE Cart
        SET quantity = :quantity
        WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
        RETURNING user_id
            ''',
                              user_id = user_id, seller_id = seller_id, product_id = product_id, quantity = quantity)

    @staticmethod
    # backend method to remove product in cart
    def remove_product_in_cart(user_id, seller_id, product_id):
        app.db.execute('''
        DELETE FROM Cart
        WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
        RETURNING user_id
            ''',
                              user_id = user_id, seller_id = seller_id, product_id = product_id)

    @staticmethod
    # backend method to check if an order could be made
    def check_order(user_id):
        cart_content = cart.get_all_cart_input(user_id)
        total_price = cart.get_total_price(user_id)
        id = user_id
        balance = app.db.execute('''
        SELECT balance
        FROM Users
        WHERE id = :id 
            ''',
                              id = id)
        #checks if user has enough balance 
        if(balance[0][0] < total_price): return 1
        else :
            # check if all products in cart have enough stock
            for c in cart_content:
                seller_id = c.seller_id
                product_id = c.product_id
                available = app.db.execute('''
                        SELECT stock
                        FROM SellsItem
                        WHERE seller_id = :seller_id AND product_id = :product_id
                        ''',
                                    seller_id = seller_id, product_id = product_id)
                if(len(available) == 0 ): return 2
                if(available[0][0] < c.quantity): return 2
        return 0

    # backend method to order all products inside cart
    @staticmethod
    def make_cart_order(user_id):
        cart_content = cart.get_all_cart_input(user_id)
        for c in cart_content:
            if c.quantity != 0:
                cart.remove_product_in_cart(c.user_id, c.seller_id, c.product_id)
                cart.purchase(c.user_id, c.seller_id, c.product_id, c.quantity, c.price_per_item)

    @staticmethod
    # backend method to order a product
    def purchase(user_id, seller_id, product_id, quantity, price):
        # finds the number of total purchases to generate order id
        total_order = app.db.execute('''
                    SELECT COUNT(order_id)
                    FROM Purchases
                    ''',)
        order_id = total_order[0][0] + 1
        payment_amount = price*quantity
        time_purchased = datetime.now(tz=None)
        time_processed = datetime(1, 1, 1, 1, 1, 1)
        status = 'Incomplete'

        # inserts in to purchases a new order
        app.db.execute('''
            INSERT INTO Purchases(order_id, product_id, buyer_id, seller_id, payment_amount, quantity,time_purchased, time_processed, status)
            VALUES(:order_id, :product_id, :buyer_id, :seller_id, :payment_amount, :quantity, :time_purchased, :time_processed, :status) 
            RETURNING order_id
            ''',
                              order_id = order_id, buyer_id = user_id, seller_id=seller_id, product_id = product_id, payment_amount = payment_amount, quantity=quantity, time_purchased=time_purchased, time_processed = time_processed, status = status)
        
        # deduct purchases quantity from seller's stock
        app.db.execute('''
        UPDATE SellsItem
        SET stock = stock - :quantity
        WHERE seller_id = :seller_id AND product_id = :product_id 
        RETURNING product_id
            ''',
                              seller_id = seller_id, product_id = product_id, quantity = quantity)
        
        # deduct total payment amount from buyer's account
        app.db.execute('''
        UPDATE Users
        SET balance = balance - :payment_amount
        WHERE id = :user_id
        RETURNING balance
            ''',
                              payment_amount = payment_amount, user_id = user_id)
        
        # add total payment amount to seller's account
        app.db.execute('''
        UPDATE Users
        SET balance = balance + :payment_amount
        WHERE id = :seller_id
        RETURNING balance
            ''',
                              payment_amount = payment_amount, seller_id = seller_id)

    # backend method to apply 10% promotion on a specific product on a cart
    @staticmethod
    def apply_promo(code, user_id, seller_id, product_id):
        # check if product is available 
        available = app.db.execute('''
                        SELECT stock
                        FROM SellsItem
                        WHERE seller_id = :seller_id AND product_id = :product_id
                        ''',
                                    seller_id = seller_id, product_id = product_id)

        if(len(available) != 0 ):    
            # if user enters an eligible code, apply 10% promotion
            if(code.lower() == 'holiday' or  code.lower() == 'thanksgiving' or code.lower() == 'duke' or code.lower() == 'black friday'):
                price_per_item = cart.get_product_price(product_id, seller_id)
                print(price_per_item)
                # update row with 10% discounted price
                app.db.execute('''
                UPDATE Cart
                SET price_per_item = 0.9*price_per_item
                WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id AND price_per_item = :price_per_item
                RETURNING user_id
                ''',
                              user_id = user_id, seller_id = seller_id, product_id = product_id, price_per_item = price_per_item)

    # backend method to apply 10% promotion on all cart products
    @staticmethod
    def apply_promo_cart(code, user_id):
        cart_content = cart.get_all_cart_input(user_id)
        for c in cart_content:
            cart.apply_promo(code, user_id, c.seller_id, c.product_id)


    # method to get price of a product
    @staticmethod
    def get_product_price(product_id, seller_id):
        price_per_item = app.db.execute('''
            SELECT price
            FROM SellsItem
            WHERE product_id = :product_id AND seller_id = :seller_id
            ''',
                              product_id = product_id, seller_id = seller_id)
        return price_per_item[0][0]

