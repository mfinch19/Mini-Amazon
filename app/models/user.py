from flask_login import UserMixin
from flask_login import current_user
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, balance, zip, street):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.zip = zip
        self.street = street

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, balance, zip, street
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, mailingaddress, zipcode, balance):
        get_new_id = app.db.execute("""
                    SELECT COUNT(id)
                    FROM Users
                    """)
        highest_id = get_new_id[0][0]
        try:
            rows = app.db.execute("""
INSERT INTO Users(id, email, password, firstname, lastname, balance, zip, street)
VALUES(:id, :email, :password, :firstname, :lastname, 0, :zip, :street)
RETURNING :id
""",
                                  id=highest_id,
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname,
                                  balance=balance,
                                  zip=zipcode,
                                  street=mailingaddress)
            #id = rows[0][0]
            return User.get(id)
        except Exception as e:
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, balance, zip, street
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def withdraw_balance(request):
        amount = request.form["withdrawal-amount"]  
        with_amount = float(amount)
        user_id = current_user.id
        curr_balance = float(current_user.balance)

        final_balance = 0.00

        if(with_amount > curr_balance):
            final_balance = 0.00
        elif(with_amount == curr_balance):
            final_balance = 0.00
        else:
            final_balance = curr_balance - with_amount
    
        rows = app.db.execute("""
        UPDATE Users
        SET balance = cast(:balance as decimal)
        WHERE id = :id
        RETURNING id
        """,
                             id=user_id,
                             balance=final_balance)
        return True
    
    @staticmethod
    def add_balance(request):
        amount = request.form["add-amount"]  
        add_amount = float(amount)
        user_id = current_user.id
        curr_balance = float(current_user.balance)

        final_balance = curr_balance + add_amount
    
        rows = app.db.execute("""
        UPDATE Users
        SET balance = cast(:balance as decimal)
        WHERE id = :id
        RETURNING id
        """,
                             id=user_id,
                             balance=final_balance)
        return True

    @staticmethod
    def update_account_info(request):
        user_id = current_user.id
        fname = request.form["fname-value"]
        lname = request.form["lname-value"]
        email = request.form["email-value"]
        street = request.form["street-value"]
        zip = request.form["zip-value"]
    
        rows = app.db.execute("""
        UPDATE Users
        SET email = :email, firstname = :firstname, lastname = :lastname, zip = :zip, street = :street
        WHERE id = :id
        RETURNING id
        """,
                            email=email,
                            firstname=fname,
                            lastname=lname,
                            zip=zip,
                            street=street,
                            id=user_id)
        return True

    @staticmethod
    def password_match(email, password):
        rows = app.db.execute("""
SELECT password, id, email
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return False
        else:
            return True

    @staticmethod
    def update_password(newPassword):
        user_id = current_user.id
        try:
            rows = app.db.execute("""
            UPDATE Users
            SET password = :password
            WHERE id = :id
            RETURNING id
            """,
                                  id=user_id,
                                  password=generate_password_hash(newPassword))
            return User.get(id)
        except Exception as e:
            return None
