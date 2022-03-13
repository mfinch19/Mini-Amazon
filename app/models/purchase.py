from datetime import datetime, timedelta
from flask import current_app as app

class SellerTransaction:
    def __init__(self, order_id, product_id, buyer_id, seller_id, buyer_name, payment_amount, quantity, time_purchased, time_processed, status, address):
        self.order_id = order_id
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.buyer_name = buyer_name
        self.payment_amount = payment_amount
        self.quantity = quantity
        self.time_purchased = time_purchased
        self.time_processed = time_processed
        self.status = status
        self.address = address

    @staticmethod
    def get_all_by_seller_id(seller_id, complete):
            if complete: 
                rows = app.db.execute('''
                SELECT p.order_id, p.product_id, p.buyer_id, p.seller_id, CONCAT(s.firstname, ' ', s.lastname), p.payment_amount, p.quantity, p.time_purchased, p.time_processed,p.status, u.street
                FROM Purchases p, Users u, Users s
                WHERE seller_id = :seller_id AND status=:status AND u.id=p.buyer_id AND s.id=p.buyer_id
                ORDER BY time_purchased DESC
                ''',
                                                seller_id=seller_id,
                                                status="Complete")
                return [SellerTransaction(*row) for row in rows] if rows else None
            else: 
                rows = app.db.execute('''
                SELECT p.order_id, p.product_id, p.buyer_id, p.seller_id, CONCAT(s.firstname, s.lastname), p.payment_amount, p.quantity, p.time_purchased, p.time_processed,p.status, u.street
                FROM Purchases p, Users u, Users s
                WHERE seller_id = :seller_id AND status=:status AND u.id=p.buyer_id AND s.id=p.buyer_id
                ORDER BY time_purchased DESC
                ''',
                                                seller_id=seller_id,
                                                status="Incomplete")
                return [SellerTransaction(*row) for row in rows] if rows else None


    @staticmethod
    def count(seller_id, complete):
            if complete: 
                rows = app.db.execute('''
                SELECT COUNT(seller_id)
                FROM Purchases 
                WHERE seller_id = :seller_id AND status=:status
                ''',
                                                seller_id=seller_id,
                                                status="Complete")
                return rows[0][0]
            else: 
                rows = app.db.execute('''
                SELECT COUNT(seller_id)
                FROM Purchases 
                WHERE seller_id = :seller_id AND status=:status
                ''',
                                                seller_id=seller_id,
                                                status="Incomplete")
                return rows[0][0]



class Purchase:
    def __init__(self, order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status):
        self.order_id = order_id
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.payment_amount = payment_amount
        self.quantity = quantity
        self.time_purchased = time_purchased
        self.time_processed = time_processed
        self.status = status

    @staticmethod
    def get(order_id):
        rows = app.db.execute('''
SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status
FROM Purchases
WHERE order_id = :order_id
''',
                              order_id=order_id)
        return Purchase(*(rows[0])) if rows else None


    @staticmethod
    def get_all_by_seller_id(seller_id, complete):
        if complete: 
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed,status
            FROM Purchases
            WHERE seller_id = :seller_id AND status=:status
            ORDER BY time_purchased DESC
            ''',
                                            seller_id=seller_id,
                                            status="Complete")
            return [Purchase(*row) for row in rows] if rows else None
        else: 
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed,status
            FROM Purchases
            WHERE seller_id = :seller_id AND status=:status
            ORDER BY time_purchased DESC
            ''',
                                            seller_id=seller_id,
                                            status="Incomplete")
            return [Purchase(*row) for row in rows] if rows else None



    @staticmethod
    def get_all_by_buyer_id(buyer_id, order_id = None):

        if order_id is None:
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed,status
            FROM Purchases
            WHERE buyer_id = :buyer_id
            ORDER BY time_purchased DESC
            ''',
                                          buyer_id=buyer_id)
        else:
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status
            FROM Purchases
            WHERE buyer_id = :buyer_id AND order_id = :order_id
            ORDER BY time_purchased DESC
            ''',
                                          buyer_id=buyer_id,
                                          order_id=order_id)

        return [Purchase(*row) for row in rows] if rows else None

    @staticmethod
    def get_all_by_buyer_id_since(buyer_id, since):
        rows = app.db.execute('''
SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status
FROM Purchases
WHERE buyer_id = :buyer_id
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              buyer_id=buyer_id,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_seller_id(seller_id, complete):
        if complete: 
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed,status
            FROM Purchases
            WHERE seller_id = :seller_id AND status=:status
            ORDER BY time_purchased DESC
            ''',
                                            seller_id=seller_id,
                                            status="Complete")
            return [Purchase(*row) for row in rows] if rows else None
        else: 
            rows = app.db.execute('''
            SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed,status
            FROM Purchases
            WHERE seller_id = :seller_id AND status=:status
            ORDER BY time_purchased DESC
            ''',
                                            seller_id=seller_id,
                                            status="Incomplete")
            return [Purchase(*row) for row in rows] if rows else None


    @staticmethod
    def update_order_status(buyer_id):
        status = 'Complete'
        time = datetime.now(tz=None) - timedelta(weeks= 2 )

        app.db.execute('''
            Update Purchases
            SET status = :status
            WHERE buyer_id = :buyer_id AND time_purchased <= :time
            RETURNING buyer_id
            ''',
                              buyer_id=buyer_id,
                              status = status,
                              time=time)

    @staticmethod
    def complete_order_manual(order_id):
        app.db.execute('''
            Update Purchases
            SET status = :status
            WHERE order_id = :order_id
            RETURNING status
            ''',
                              order_id=order_id,
                              status='Complete')


    @staticmethod
    def get_all_by_buyer_id_completed(buyer_id):
        status = 'Complete'

        rows = app.db.execute('''
SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status
FROM Purchases
WHERE buyer_id = :buyer_id
AND status = :status
ORDER BY time_purchased DESC
''',
                              buyer_id=buyer_id,
                              status=status)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_buyer_id_incomplete(buyer_id):
        status = 'Incomplete'

        rows = app.db.execute('''
SELECT order_id, product_id, buyer_id, seller_id, payment_amount, quantity, time_purchased, time_processed, status
FROM Purchases
WHERE buyer_id = :buyer_id
AND status = :status
ORDER BY time_purchased DESC
''',
                              buyer_id=buyer_id,
                              status=status)
        return [Purchase(*row) for row in rows]
