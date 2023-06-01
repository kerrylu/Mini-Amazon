from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname
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
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address)
VALUES(:email, :password, :firstname, :lastname, :address)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, 
                                  lastname=lastname,
                                  address=address)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    def get_all():
        rows = app.db.execute("""
                                SELECT id, email, firstname, lastname
                                FROM Users
                                """)
        return rows if rows else None


    @staticmethod
    def sort_purchases_date_desc(id):
        rows = app.db.execute("""
                                SELECT O.id,
                                O.order_total,
                                COUNT(P.product_id),
                                O.order_fulfilled_datetime
                                FROM Orders O
                                JOIN Purchases P ON O.id = P.order_id
                                JOIN Products Pr on Pr.id = P.product_id
                                WHERE user_id = :id
                                GROUP BY O.id 
                                ORDER BY O.order_fulfilled_datetime DESC
                                """,
                              id=id)
        return rows if rows else None

    @staticmethod
    def sort_purchases_date_asc(id):
        rows = app.db.execute("""
                                SELECT O.id,
                                O.order_total,
                                COUNT(P.product_id),
                                O.order_fulfilled_datetime
                                FROM Orders O
                                JOIN Purchases P ON O.id = P.order_id
                                JOIN Products Pr on Pr.id = P.product_id
                                WHERE user_id = :id
                                GROUP BY O.id 
                                ORDER BY O.order_fulfilled_datetime ASC
                                """,
                              id=id)
        return rows if rows else None

    @staticmethod
    def search_by_name(name):
        rows = app.db.execute('''
                                SELECT *
                                FROM Products
                                WHERE name LIKE '%' || :name || '%'
                                    AND id IN (SELECT product_id
                                            FROM Inventory
                                            WHERE quantity >= 1)
                            ''',
                              name=name)
        return [Product(*row) for row in rows]

    @staticmethod
    def sort_purchases_price_asc(id):
        rows = app.db.execute("""
                                SELECT O.id,
                                O.order_total,
                                COUNT(P.product_id),
                                O.order_fulfilled_datetime
                                FROM Orders O
                                JOIN Purchases P ON O.id = P.order_id
                                JOIN Products Pr on Pr.id = P.product_id
                                WHERE user_id = :id
                                GROUP BY O.id 
                                ORDER BY O.order_total ASC
                                """,
                              id=id)
        return rows if rows else None

    @staticmethod
    def sort_purchases_price_desc(id):
        rows = app.db.execute("""
                                SELECT O.id,
                                O.order_total,
                                COUNT(P.product_id),
                                O.order_fulfilled_datetime
                                FROM Orders O
                                JOIN Purchases P ON O.id = P.order_id
                                JOIN Products Pr on Pr.id = P.product_id
                                WHERE user_id = :id
                                GROUP BY O.id 
                                ORDER BY O.order_total DESC
                                """,
                              id=id)
        return rows if rows else None
    
    # @staticmethod
    # def sort_purchases_price_desc(id):
    #     rows = app.db.execute("""
    #                             SELECT Pr.id, 
    #                                 Pr.name, 
    #                                 Pr.category, 
    #                                 Pr.description, 
    #                                 Pr.price, 
    #                                 P.item_fulfilled_datetime, 
    #                                 Pr.image 
    #                             FROM Orders O
    #                             JOIN Purchases P ON O.id = P.order_id
    #                             JOIN Products Pr on Pr.id = P.product_id
    #                             WHERE user_id = :id
    #                             ORDER BY Pr.price DESC
    #                             """,
    #                           id=id)
    #     return rows if rows else None

    @staticmethod
    def sort_purchases_id(id):
        rows = app.db.execute("""
                                SELECT O.id,
                                O.order_total,
                                COUNT(P.product_id),
                                O.order_fulfilled_datetime
                                FROM Orders O
                                JOIN Purchases P ON O.id = P.order_id
                                JOIN Products Pr on Pr.id = P.product_id
                                WHERE user_id = :id
                                GROUP BY O.id 
                                ORDER BY O.id
                                """,
                              id=id)
        return rows if rows else None

    
    def get_id(self):
        return int(self.id)

    def get_accountinfo(id):
            rows = app.db.execute("""
                                    SELECT id,
                                    email,
                                    firstname,
                                    lastname,
                                    address,
                                    balance
                                    FROM Users
                                    WHERE id = :id
                                    """,
                                id=id)
            return rows if rows else None

    def update_accountinfo(id, email, first, last, location, balance):
            rows = app.db.execute("""
                                    Select *
                                    FROM Users
                                    WHERE not id = :id AND email = :email
                                    """,
                                id=id, email = email)
            
            if not rows:
                app.db.execute("""
                                    UPDATE Users
                                    SET email = :email,
                                    firstname = :first,
                                    lastname = :last,
                                    address = :location,
                                    balance = :balance
                                    WHERE id = :id
                                    """,
                                id=id, email = email, first=first, last=last, location=location, balance = balance)
            # return rows if rows else None
        
    def update_user_pwd(id, password):
           
            app.db.execute("""
                                    UPDATE Users
                                    SET password = :password
                                    WHERE id = :id
                                    """,
                                id=id, password=generate_password_hash(password))

    def get_seller_reviews(id):
            rows = app.db.execute("""
                                    SELECT user_id,
                                    description,
                                    rating,
                                    upvotes,
                                    datetime
                                    FROM SellerReviews
                                    WHERE seller_id = :id
                                    """,
                                id=id)
            return rows if rows else None
    
    def isSeller(id):
            rows = app.db.execute("""
                                    SELECT *
                                    FROM Sellers
                                    WHERE id = :id
                                    """,
                                id=id)
            return rows if rows else None

    def newSeller(id):
        app.db.execute("""INSERT INTO Sellers VALUES (:id)""", id=id)
        return 0



