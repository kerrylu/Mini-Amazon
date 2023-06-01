from flask import current_app as app
from .inventory import Inventory
from .user import User
from flask import flash


class Order:
    def __init__(self, id, user_id, user_address, order_total, datetime, order_fulfilled_datetime):
        self.id = id
        self.user_id = user_id
        self.user_address = user_address
        self.order_total = order_total
        self.datetime = datetime
        self.order_fulfilled_datetime = order_fulfilled_datetime

    @staticmethod
    def add_order(user_id, user_address, order_total, datetime):
        row = app.db.execute('''SELECT MAX(Orders.id) as MAX_ID FROM Orders''')
        id = row[0][0] + 1

        app.db.execute(
            ''' INSERT INTO Orders(id, user_id, user_address, order_total, datetime, order_fulfilled_datetime)
            VALUES(:id, :user_id, :user_address, :order_total, :datetime, :order_fulfilled_datetime)
            RETURNING *
            ''', id=id, user_id=user_id, user_address=user_address, order_total=order_total, datetime=datetime, order_fulfilled_datetime=None)
        return id
    
    @staticmethod
    def get_address(user_id):
        address = app.db.execute(
        '''
        SELECT address
        FROM Users
        WHERE id = :user_id
        ''', user_id=user_id)
        return address

    @staticmethod
    def get_status(id):
        status = app.db.execute(
            '''
            SELECT order_fulfilled_datetime
            FROM Orders
            WHERE id = :id
            ''', id=id)
        return status
    
    @staticmethod
    def get_user(id):
        user_id = app.db.execute(
            '''
            SELECT user_id
            FROM Orders
            WHERE id = :id
            ''', id=id)
        return user_id[0][0]

    @staticmethod
    def fulfill_order(id,ful_time):
        app.db.execute(
            '''
            UPDATE Orders
            SET order_fulfilled_datetime = :ful_time
            WHERE id = :id
            ''', id=id,ful_time=ful_time)
