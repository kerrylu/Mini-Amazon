from flask import current_app as app


class Review:
    """
    This is just a TEMPLATE for Review, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, review_time, review_content):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.review_time = review_time
        self.review_content = review_content

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, review_time, review_content
FROM Review
WHERE id = :id
''',
                              id=id)
        return Review(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, review_time, review_content
FROM Review
WHERE uid = :uid
AND review_time >= :since
ORDER BY review_time DESC
''',
                              uid=uid,
                              since=since)
        return [Review(*row) for row in rows]

    def get_recent_5_reviews(uid):
        rows = app.db.execute(
            """SELECT id, pid, review_time, review_content
            FROM Review
            WHERE uid = :uid
            ORDER BY review_time DESC
            LIMIT 5 """, uid = uid
        )
        return rows

    @staticmethod
    def upvote(user_id, product_id, seller_id):
        rows = app.db.execute('''
UPDATE ProductReviews
SET upvotes = upvotes + 1
WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id
''',
                    user_id=user_id, product_id=product_id, seller_id=seller_id)

class ProductReview:
    def __init__(self, uid, sid, user_firstname, user_lastname, seller_firstname, seller_lastname, description, rating, upvotes, time):
        self.uid = uid
        self.sid = sid
        self.user_firstname = user_firstname
        self.user_lastname = user_lastname
        self.seller_firstname = seller_firstname
        self.seller_lastname = seller_lastname
        self.description = description
        self.rating = rating
        self.upvotes = upvotes
        self.time = time

    @staticmethod
    def get_by_pid(pid):
        rows = app.db.execute('''
SELECT r.user_id , r.seller_id, u.firstname as user_firstname, u.lastname as user_lastname, s.firstname seller_firstname, s.lastname seller_lastname, r.description, r.rating, r.upvotes, r.datetime, r.product_id
FROM ProductReviews AS r, Users AS u, Users AS s
WHERE r.product_id = :pid
    AND r.user_id = u.id
    AND r.seller_id = s.id
''',
                              pid=pid)
        return rows
        return [ProductReview(*row) for row in rows]