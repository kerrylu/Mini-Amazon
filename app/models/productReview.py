from flask import current_app as app, flash
from datetime import datetime

class ProductReview:
    def __init__(self, uid, pid, sid, description, rating, upvotes, datetime):
        self.uid = user_id
        self.pid = product_id
        self.sid = seller_id
        self.description = description
        self.rating = rating
        self.upvotes = upvotes
        self.datetime = datetime
    

    @staticmethod
    def add_review(uid, pid, sid, description, rating):
        purchase = app.db.execute(
            """
            SELECT product_id FROM Purchases, Orders
            WHERE Purchases.order_id = Orders.id 
            AND user_id = :uid AND product_id =:pid

            """, uid = uid, pid = pid
        )

        if purchase == []:
            flash("You can only write a review if you have purchased the item.")
            return 0
        
        reviews = app.db.execute(
            """
            SELECT product_id FROM ProductReviews
            WHERE user_id = :uid AND product_id = :pid AND seller_id = :sid
            """, uid = uid, pid = pid, sid = sid
        )

        if reviews != []:
            flash("Review already exists for this item")
            return 1
        
        time = datetime.now()
        app.db.execute(
            """
            INSERT INTO ProductReviews(user_id, seller_id, product_id, description, rating, upvotes, datetime)
            VALUES(:uid, :sid, :pid, :description, :rating, 0, :time)
            RETURNING user_id
            """, uid = uid, pid = pid, sid = sid, rating = rating, description = description, time = time
        )

        flash("Added review!")
        return True

    @staticmethod
    def get_five_most_recent(user_id):
        rows = app.db.execute(
            """SELECT product_id, seller_id, description, rating, upvotes, datetime
            FROM ProductReviews
            WHERE user_id = :user_id
            ORDER BY datetime DESC
            LIMIT 5 """, user_id = user_id
        )
        test = app.db.execute(
            """SELECT *
            FROM ProductReviews
            """, user_id = user_id
        )
        #flash(test)
        return rows
        return [ProductReview(*row) for row in rows]

    @staticmethod
    def get(uid):
        reviews = app.db.execute(
            """ SELECT * FROM ProductReviews
            WHERE user_id=:uid
            ORDER BY datetime DESC
            """, uid=uid
        )
        return reviews
    
    @staticmethod
    def get_by_pid(pid):
        reviews = app.db.execute(
            """ SELECT * FROM ProductReviews
            WHERE product_id=:pid
            ORDER BY datetime DESC
            """, pid=pid
        )
        return reviews

    @staticmethod
    def update(uid, pid, sid, description, rating):
        time = datetime.now()

        app.db.execute(
            """ UPDATE ProductReviews
            SET description = :description, rating = :rating, datetime = :time
            WHERE user_id = :uid AND product_id = :pid AND seller_id = :sid
            RETURNING *
            """, description = description, rating = rating, time = time, uid = uid, pid = pid, sid = sid
        )

        return 0

    @staticmethod
    def delete(uid, pid, sid):
        time = datetime.now()

        app.db.execute(
            """ DELETE FROM ProductReviews
            WHERE user_id = :uid AND product_id = :pid AND seller_id = :sid
            RETURNING user_id
            """,  uid = uid, pid = pid, sid = sid
        )

        flash("Review Removed")
        return uid

    @staticmethod
    def get_average(pid):
        reviews = app.db.execute(
            """ SELECT AVG(rating)::numeric(10,1) as avg FROM ProductReviews
            WHERE product_id=:pid
            GROUP BY product_id
            """, pid=pid
        )
        if reviews == []:
            return 0.0
        
        return reviews[0][0]

    @staticmethod
    def count(pid):
        rows = app.db.execute(
            """ SELECT COUNT(rating) as count
            FROM ProductReviews
            WHERE product_id = :pid
            GROUP BY product_id
            """, pid = pid
        )

        if rows == [] or 0:
            return 0
        
        return rows[0][0]

    @staticmethod
    def update_image_path(pid, uid, filename):
        app.db.execute(
            """ UPDATE ProductReviews
            SET filename = :filename
            WHERE product_id=:pid and user_id=:uid
            """, filename=filename, uid=uid, pid=pid
        )
        return 0

    @staticmethod
    def get_user_product_image_path(pid, uid):
        rows = app.db.execute(
            """ SELECT filename
            FROM ProductReviews
            WHERE product_id=:pid and user_id=:uid
            """, pid=pid, uid=uid
        )
        return rows[0][0]

    @staticmethod
    def get_product_image_path(pid):
        reviews = app.db.execute(
            """ SELECT user_id, rating, description, datetime, upvotes, filename
            FROM ProductReviews
            WHERE product_id=:pid and filename is not NULL
            ORDER BY like_num DESC
            """, pid=pid
        )
        return reviews
