from flask import current_app as app
import time
import datetime as DT
    
class Inventory:
    '''
    This is just a TEMPLATE for Inventory, you should change this by adding or 
        replacing new columns, etc. for your design.
    '''
    def __init__(self, sid, pid, name, image, quantity, price):
        self.sid = sid
        self.pid = pid
        self.name = name
        self.image = image
        self.quantity = quantity
        self.price = price

    @staticmethod
    def get_by_pid(product_id):
        rows = app.db.execute('''
SELECT seller_id, product_id, name, image, quantity, price
FROM Inventory, Products
WHERE product_id = :product_id AND id = product_id
''',
                              product_id=product_id)
        return Inventory(*(rows[0])) if rows else None

    @staticmethod
    def get_by_sid(seller_id):
        rows = app.db.execute('''
SELECT seller_id, product_id, name, image, quantity, price
FROM Inventory, Products
WHERE seller_id = :seller_id AND id = product_id
''',
                              seller_id=seller_id)
        return [Inventory(*row) for row in rows]

    @staticmethod
    def auth_sid(seller_id):
        rows = app.db.execute('''
SELECT *
FROM Sellers
WHERE id = :seller_id
''',
                              seller_id=seller_id)
        return rows if rows else None

    @staticmethod
    def auth_add_new_product(product_name):
        row = app.db.execute('''SELECT * FROM Products WHERE name = :product_name''',product_name=product_name)
        return row if row else None

    @staticmethod
    def auth_add_product(seller_id, product_id):
        max = app.db.execute('''SELECT MAX(id) FROM Products''')
        maxID = max[0][0]
        if product_id > maxID:
            return None
        row = app.db.execute('''
        SELECT * FROM Inventory WHERE product_id = :product_id AND seller_id = :seller_id
        ''',seller_id=seller_id,product_id=product_id)
        if len(row) != 0:
            return None
        return max
    
    @staticmethod
    def auth_edit_product(pid, sid):
        ret = app.db.execute('''
        SELECT seller_id, product_id, name, image, quantity, price
FROM Inventory, Products
WHERE product_id=:pid AND seller_id=:sid
''', pid=pid, sid=sid)
        if ret is None:
            return None
        return Inventory(*ret[0])

    @staticmethod
    def addNewProduct(nm, cat, desc, pric, imagePath, seller_id, quantity):
        app.db.execute('''INSERT INTO Products (name, category, description, price, image) VALUES (:nm, :cat, :desc, :pric, :imagePath)''', nm=nm, cat=cat, desc=desc, pric=pric, imagePath=imagePath)
        row = app.db.execute('''SELECT MAX(id) FROM Products''')
        curID = row[0][0]
        app.db.execute('''INSERT INTO Inventory VALUES (:product_id, :seller_id, :quantity)''', product_id=curID, seller_id=seller_id, quantity=quantity)

    @staticmethod
    def addProduct(product_id, seller_id, quantity):
        app.db.execute('''
INSERT INTO Inventory VALUES (:product_id, :seller_id, :quantity)
''', product_id=product_id, seller_id=seller_id, quantity=quantity)

    @staticmethod
    def editProduct(pid, sid, quant):
        app.db.execute('''
UPDATE Inventory SET quantity=:quant WHERE product_id=:pid AND seller_id=:sid
''', pid=pid, sid=sid, quant=quant)

    @staticmethod
    def removeProduct(pid, sid):
        app.db.execute('''
DELETE FROM Inventory WHERE product_id=:pid AND seller_id=:sid
''', pid=pid, sid=sid)

    @staticmethod
    def update_inventory_quantity(seller_id, product_id, quantity):
        app.db.execute('''
            UPDATE Inventory
            SET quantity = :quantity
            WHERE seller_id = :seller_id AND product_id = :product_id
            RETURNING seller_id
        ''',
        seller_id=seller_id, product_id=product_id, quantity=quantity)
        return 0

    @staticmethod
    def delete_inventory_item(seller_id, product_id):
        app.db.execute('''
            DELETE FROM Inventory
            WHERE seller_id = :seller_id AND product_id = :product_id
            RETURNING seller_id
        ''',
        seller_id=seller_id, product_id=product_id)
        return 0

class DetailedInventory:
    def __init__(self, sid, pid, seller_firstname, seller_lastname, quantity):
        self.sid = sid
        self.pid = pid
        self.seller_firstname = seller_firstname
        self.seller_lastname = seller_lastname
        self.quantity = quantity

    @staticmethod
    def get_by_pid(product_id):
        rows = app.db.execute('''
SELECT seller_id, product_id, Users.firstname, Users.lastname, quantity
FROM Inventory, Users
WHERE Inventory.product_id = :product_id
    AND Users.id = Inventory.seller_id
''',
                              product_id=product_id)
        return [DetailedInventory(*row) for row in rows]

class OrderInfo:
    def __init__(self, uid, oid, firstname, lastname, address, orderdate, items, total, fulfill):
        self.uid = uid
        self.oid = oid
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.orderdate = orderdate
        self.items = items
        self.total = total
        self.fulfill = fulfill

    @staticmethod
    def get_orders(seller_id):
        rows = app.db.execute('''
            WITH orderGroups AS (
                SELECT order_id, SUM(quantity) AS items, SUM(quantity*price_per_unit) AS total, MAX(item_fulfilled_datetime) AS fulfill
                FROM Purchases
                WHERE seller_id = :seller_id
                GROUP BY order_id
            )
            SELECT user_id, order_id, firstname, lastname, address, datetime, items, total, fulfill
            FROM Users, Orders, orderGroups
            WHERE Users.id = user_id AND Orders.id = order_id
            ORDER BY datetime DESC
        ''',
        seller_id=seller_id)
        for ind in range(len(rows)):
            rowList = list(rows[ind])
            rowList[5] = rowList[5].strftime("%Y-%m-%d")
            endTime = DT.datetime(2038, 1, 19, 3, 14, 7)
            if rowList[8] == endTime:
                print("equal")
                rowList[8] = "No"
            rows[ind] = tuple(rowList)
        return [OrderInfo(*row) for row in rows]

class LineItem:
    def __init__(self, oid, pid, productName, quantity, fulfill):
        self.oid = oid
        self.pid = pid
        self.productName = productName
        self.quantity = quantity
        self.fulfill = fulfill
        
    
    @staticmethod
    def get_order(seller_id, order_id):
        rows = app.db.execute('''
            SELECT order_id, product_id, name, quantity, item_fulfilled_datetime
            FROM Purchases, Products
            WHERE id = product_id AND order_id = :order_id AND seller_id = :seller_id
        ''',
        order_id=order_id, seller_id=seller_id)
        for ind in range(len(rows)):
            rowList = list(rows[ind])
            endTime = DT.datetime(2038, 1, 19, 3, 14, 7)
            if rowList[4] == endTime:
                print("equal")
                rowList[4] = "No"
            rows[ind] = tuple(rowList)
        return [LineItem(*row) for row in rows]

    @staticmethod
    def fulfill_item(order_id, product_id, ful_time):
        app.db.execute('''
            UPDATE Purchases
            SET item_fulfilled_datetime = :ful_time
            WHERE order_id = :order_id AND product_id = :product_id
        ''',
        order_id=order_id, product_id=product_id, ful_time=time.strftime('%Y-%m-%d %H:%M:%S'))
        done = app.db.execute('''
            SELECT MAX(item_fulfilled_datetime)
            FROM Purchases
            WHERE order_id = :order_id
        ''',
        order_id=order_id)
        endTime = DT.datetime(2038, 1, 19, 3, 14, 7)
        if done[0][0] == endTime:
            return None
        return done[0][0]
    
