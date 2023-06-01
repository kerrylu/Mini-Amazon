from flask import current_app as app, flash
from datetime import datetime

class SellerReview:
    def __init__(self, user_id, seller_id, description, rating, upvotes, datetime):
        self.user_id = user_id
        self.seller_id = seller_id
        self.description = description
        self.rating = rating
        self.upvotes = upvotes
        self.datetime = datetime
    

    def add_review(uid, sid, description, rating):
        purchase = app.db.execute(
            """
            SELECT seller_id FROM Purchases, Orders
            WHERE Purchases.order_id = Orders.id 
            AND user_id = :uid AND seller_id = :sid

            """, uid = uid, sid = sid
        )

        if purchase == []:
            flash("You can only write a review if you have purchased from the seller.")
            return 0
        
        reviews = app.db.execute(
            """
            SELECT seller_id FROM SellerReviews
            WHERE user_id = :uid AND seller_id = :sid
            """, uid = uid, sid = sid
        )

        if reviews != []:
            flash("Review already exists for this seller")
            return 1
        
        time = datetime.now()
        app.db.execute(
            """
            INSERT INTO SellerReviews(user_id, seller_id, description, rating, upvotes, datetime)
            VALUES(:uid, :sid, :description, :rating, 0, :time)
            RETURNING user_id
            """, uid = uid, sid = sid, rating = rating, description = description, time = time
        )

        flash("Added review!")
        return True

    @staticmethod
    def get_five_most_recent(user_id):
        rows = app.db.execute(
            """SELECT seller_id, description, rating, upvotes, datetime
            FROM SellerReviews
            WHERE user_id = :user_id
            ORDER BY datetime DESC
            LIMIT 5 """, user_id = user_id
        )
        return rows
        return [SellerReview(*row) for row in rows]

    @staticmethod
    def get(uid):
        reviews = app.db.execute(
            """ SELECT * FROM SellerReviews
            WHERE user_id=:uid
            ORDER BY datetime DESC
            """, uid=uid
        )
        
        return reviews

    @staticmethod
    def get_by_sid(sid):
        reviews = app.db.execute(
            """ SELECT * FROM SellerReviews
            WHERE seller_id=:sid
            ORDER BY datetime DESC
            """, sid=sid
        )
        
        return reviews

    @staticmethod
    def update(uid, sid, description, rating):
        time = datetime.now()

        app.db.execute(
            """ UPDATE SellerReviews
            SET description = :description, rating = :rating, datetime = :time
            WHERE user_id = :uid AND seller_id = :sid
            RETURNING *
            """, description = description, rating = rating, time = time, uid = uid, sid = sid
        )

        return 0

    @staticmethod
    def delete(uid, sid):
        time = datetime.now()

        app.db.execute(
            """ DELETE FROM SellerReviews
            WHERE user_id = :uid AND seller_id = :sid
            RETURNING user_id
            """,  uid = uid, sid = sid
        )

        flash("Review Removed")
        return uid

    @staticmethod
    def get_average(sid):
        reviews = app.db.execute(
            """ SELECT AVG(rating)::numeric(10,1) as avg FROM SellerReviews
            WHERE seller_id=:sid
            GROUP BY seller_id
            """, sid=sid
        )
        if reviews == []:
            return 0.0

        return reviews[0][0]
        
    @staticmethod
    def count(sid):
        rows = app.db.execute(
            """ SELECT COUNT(rating) as count
            FROM SellerReviews
            WHERE seller_id = :sid
            GROUP BY seller_id
            """, sid = sid
        )

        if rows == [] or 0:
            return 0
        return rows[0][0]