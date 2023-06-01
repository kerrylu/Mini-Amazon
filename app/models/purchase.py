from flask import current_app as app
from .cart import Cart


class Purchase:
    def __init__(self, id, sid, uid, pid, quantity, price_per_unit, time_purchased):
        self.id = id
        self.sid = sid
        self.uid = uid
        self.pid = pid
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT Purchases.order_id, Users.id as seller_id, CONCAT(Users.firstname, ' ', Users.lastname) as seller_name, Products.id,
            Products.name, Purchases.quantity, Purchases.price_per_unit, Purchases.quantity * Purchases.price_per_unit as total_price
            FROM Purchases, Products, Users
            WHERE Purchases.order_id = :id
            AND Users.id = Purchases.seller_id
            AND Products.id = Purchases.product_id
            AND Products.price = Purchases.price_per_unit
            ''',
                              id=id)
        return [Cart(*row) for row in rows] if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, item_fulfilled_datetime
FROM Purchases
WHERE uid = :uid
AND item_fulfilled_datetime >= :since
ORDER BY item_fulfilled_datetime DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def add_purchase(id, sid, pid, quantity, price_per_unit, time_fulfilled, user_id):
        app.db.execute(
            ''' INSERT INTO Purchases(order_id, seller_id, product_id, quantity, price_per_unit, item_fulfilled_datetime)
            VALUES(:id, :sid, :pid, :quantity, :price_per_unit, :time_fulfilled)
            RETURNING *
            ''', id=id, sid=sid, pid=pid, quantity=quantity, price_per_unit=price_per_unit, time_fulfilled=time_fulfilled)

        user_balance = app.db.execute('''
            SELECT balance
            FROM Users
            WHERE id = :user_id
        ''', user_id=user_id)

        app.db.execute(
            '''
            UPDATE Users
            SET balance = :balance - (:price_per_unit * :quantity)
            WHERE id = :user_id
            ''', user_id=user_id, balance=user_balance[0][0], price_per_unit=price_per_unit, quantity=quantity)

        seller_balance = app.db.execute('''
            SELECT balance
            FROM Users
            WHERE id = :seller_id
        ''', seller_id=sid)
        
        app.db.execute(
            '''
            UPDATE Users
            SET balance = :balance + (:price_per_unit * :quantity)
            WHERE id = :seller_id
            ''', seller_id=sid, balance=seller_balance[0][0], price_per_unit=price_per_unit, quantity=quantity)

        app.db.execute(
            '''
            UPDATE Inventory
            SET quantity = quantity - :quantity
            WHERE product_id = :product_id AND seller_id = :seller_id
            ''', quantity=quantity, product_id=pid, seller_id=sid)
        return id
