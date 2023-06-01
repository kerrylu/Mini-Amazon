from flask import current_app as app

class Cart:
    """
    This is just a TEMPLATE for Cart, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, user_id, seller_id, seller_name, product_id, product_name, quantity, price_per_unit, total_price):
        self.user_id = user_id
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.total_price = total_price

    @staticmethod
    def get_all_in_cart(user_id):
        rows = app.db.execute('''
            SELECT CartEntries.user_id, Users.id as seller_id, CONCAT(Users.firstname, ' ', Users.lastname) as seller_name, Products.id, 
            Products.name, CartEntries.quantity, CartEntries.price_per_unit, CartEntries.quantity * CartEntries.price_per_unit as total_price
            FROM CartEntries, Products, Users
            WHERE CartEntries.user_id = :user_id
            AND Users.id <> CartEntries.user_id
            AND Users.id = CartEntries.seller_id
            AND Products.id = CartEntries.product_id
            AND Products.price = CartEntries.price_per_unit
            AND CartEntries.is_saved_for_later = 'false'
        ''',
        user_id=user_id)
        return [Cart(*row) for row in rows]

    @staticmethod
    def get_all_in_wishlist(user_id):
        rows = app.db.execute('''
            SELECT CartEntries.user_id, Users.id as seller_id, CONCAT(Users.firstname, ' ', Users.lastname) as seller_name, Products.id, 
            Products.name, CartEntries.quantity, CartEntries.price_per_unit, CartEntries.quantity * CartEntries.price_per_unit as total_price
            FROM CartEntries, Products, Users
            WHERE CartEntries.user_id = :user_id
            AND Users.id <> CartEntries.user_id
            AND Users.id = CartEntries.seller_id
            AND Products.id = CartEntries.product_id
            AND Products.price = CartEntries.price_per_unit
            AND CartEntries.is_saved_for_later = 'true'
        ''',
        user_id=user_id)
        return [Cart(*row) for row in rows]

    @staticmethod
    def update_quantity(user_id, seller_id, product_id, quantity):
        app.db.execute('''
            UPDATE CartEntries
            SET quantity = :quantity
            WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
            RETURNING user_id
        ''',
        user_id=user_id, seller_id=seller_id, product_id=product_id, quantity=quantity)

    @staticmethod
    def delete_item(user_id, seller_id, product_id):
        app.db.execute('''
            DELETE FROM CartEntries
            WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
            RETURNING user_id
        ''',
        user_id=user_id, seller_id=seller_id, product_id=product_id)

    @staticmethod
    def add_wishlist_item_to_cart(user_id, seller_id, product_id):
        app.db.execute('''
            UPDATE CartEntries
            SET is_saved_for_later = 'false'
            WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
            RETURNING user_id
        ''',
        user_id=user_id, seller_id=seller_id, product_id=product_id)

    @staticmethod
    def get_total_price(user_id):
        count = 0
        user_cart = Cart.get_all_in_cart(user_id)
        for item in user_cart:
            count += item.total_price
        return count

    @staticmethod
    def check_status(user_id):
        all_products = Cart.get_all_in_cart(user_id)
        total_price = Cart.get_total_price(user_id)
        balance = app.db.execute('''
            SELECT balance
            FROM Users
            WHERE id = :user_id
        ''',
                            user_id=user_id)
        if balance[0][0] < total_price:
            return -1
        else:
            for p in all_products:
                if_available = app.db.execute('''
                    SELECT quantity
                    FROM Inventory
                    WHERE seller_id = :seller_id AND product_id = :product_id
                ''',
                            seller_id=p.seller_id, product_id=p.product_id)
            if not if_available or if_available[0][0] < p.quantity:
                return -2
        return 0

    @staticmethod
    def clear_cart(user_id):
        all_products = Cart.get_all_in_cart(user_id)
        for p in all_products:
            if p.quantity > 0:
                Cart.delete_item(user_id, p.seller_id, p.product_id)
    def add_to_cart(user_id, seller_id, product_id, quantity, price):
        rows = app.db.execute('''
        SELECT *
        FROM CartEntries
        WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id AND is_saved_for_later = 'false'
        ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id)
        if rows:
            app.db.execute('''
                UPDATE CartEntries
                SET quantity = quantity + :quantity, is_saved_for_later = 'false'
                WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
                RETURNING user_id
            ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id, quantity=quantity)
        else:
            app.db.execute('''
                INSERT INTO CartEntries(user_id, seller_id, product_id, quantity, price_per_unit, is_saved_for_later)
                VALUES (:user_id, :seller_id, :product_id, :quantity, :price, 'false')
            ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id, quantity=quantity, price=price)

    @staticmethod
    def add_to_wishlist(user_id, seller_id, product_id, quantity, price):
        rows = app.db.execute('''
        SELECT *
        FROM CartEntries
        WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
        ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id)
        if rows:
            app.db.execute('''
                UPDATE CartEntries
                SET quantity = quantity + :quantity, is_saved_for_later = 'true'
                WHERE user_id = :user_id AND seller_id = :seller_id AND product_id = :product_id
                RETURNING user_id
            ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id, quantity=quantity)
        else:
            app.db.execute('''
                INSERT INTO CartEntries(user_id, seller_id, product_id, quantity, price_per_unit, is_saved_for_later)
                VALUES (:user_id, :seller_id, :product_id, :quantity, :price, 'true')
            ''',
            user_id=user_id, seller_id=seller_id, product_id=product_id, quantity=quantity, price=price)