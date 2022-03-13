from flask import current_app as app
from flask_login import current_user
from sqlalchemy import exc




class Category:
    def __init__(self, cat_name, description):
        self.cat_name = cat_name
        self.description = description

    # def __repr__():
    #     return ""

    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT * FROM Category 
        ''',
        )
        return [Category(*row) for row in rows]
