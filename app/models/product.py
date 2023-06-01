from flask import current_app as app


class Product:
    def __init__(self, pid, name, category, description, price, image):
        self.pid = pid
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.image = image

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE id IN (SELECT product_id
            FROM Inventory
            WHERE quantity >= 1)
'''
                              )
        return [Product(*row) for row in rows]

    @staticmethod
    def most_expensive(k):
        rows = app.db.execute('''
SELECT *
FROM Products
ORDER BY price DESC
LIMIT :k
''',
                              k=k)
        return [Product(*row) for row in rows]

class ProductSummary:
    def __init__(self, pid, name, price, image, avg_review, avail_quantity):
        self.pid = pid
        self.name = name
        self.price = price
        self.image = image
        self.avg_review = avg_review
        self.avail_quantity = avail_quantity

    @staticmethod
    def get_all():
        rows = app.db.execute('''
WITH inv AS(
    SELECT product_id, SUM(quantity) AS avail_quantity
    FROM Inventory
    GROUP BY product_id
)
SELECT Products.id as id, Products.name as name, Products.price as price, Products.image as image, ROUND(AVG(rating),2) as avg_review, avail_quantity
FROM Products, ProductReviews, inv
WHERE Products.id = ProductReviews.product_id
    AND Products.id = inv.product_id
    AND avail_quantity > 0
GROUP BY Products.id, Products.name, Products.price, Products.image, avail_quantity
ORDER BY id ASC
'''
                              )
        return [ProductSummary(*row) for row in rows]

    @staticmethod
    def get_by_search(search, searchBy, sortBy, category, filterQuantity, filterPrice):
        quantMin = 0
        quantMax = 100000
        priceMin = 0
        priceMax = 500
        if filterQuantity == 'greater100':
            quantMin = 100
            quantMax = 100000
        elif filterQuantity == "50-100":
            quantMin = 50
            quantMax = 100
        elif filterQuantity == "less50":
            quantMin = 0
            quantMax = 50

        if filterPrice == "400-500":
            priceMin = 400
            priceMax = 500
        elif filterPrice == "300-400":
            priceMin = 300
            priceMax = 400
        elif filterPrice == "200-300":
            priceMin = 200
            priceMax = 300
        elif filterPrice == "100-200":
            priceMin = 100
            priceMax = 200
        elif filterPrice == "less100":
            priceMin = 0
            priceMax = 100
        
        if searchBy == "Name":
            rows = app.db.execute('''
            WITH inv AS(
                SELECT product_id, SUM(quantity) AS avail_quantity
                FROM Inventory
                GROUP BY product_id
            )
            SELECT Products.id as id, Products.name as name, Products.price as price, Products.image as image, ROUND(AVG(rating),2) as avg_review, avail_quantity
            FROM Products, ProductReviews, inv
            WHERE Products.id = ProductReviews.product_id
                AND Products.id = inv.product_id
                AND Products.name LIKE '%' || :search || '%'
                AND Products.category LIKE '%' || :category || '%'
                AND avail_quantity > :quantMin
                AND avail_quantity < :quantMax
                AND Products.price > :priceMin
                AND Products.price < :priceMax
            GROUP BY Products.id, Products.name, Products.price, Products.image, avail_quantity
            ORDER BY
                CASE WHEN :sortBy = 'default' THEN id END ASC,
                CASE WHEN :sortBy = 'highToLow' THEN price END DESC,
                CASE WHEN :sortBy = 'lowToHigh' THEN price END ASC,
                CASE WHEN :sortBy = 'avgRev' THEN AVG(rating) END DESC,
                CASE WHEN :sortBy = 'availQuant' THEN avail_quantity END DESC
            ''', search=search, sortBy=sortBy, category=category, quantMin=quantMin, quantMax=quantMax, priceMin=priceMin, priceMax=priceMax)
            return [ProductSummary(*row) for row in rows]
        elif searchBy == "Description":
            rows = app.db.execute('''
            WITH inv AS(
                SELECT product_id, SUM(quantity) AS avail_quantity
                FROM Inventory
                GROUP BY product_id
            )
            SELECT Products.id as id, Products.name as name, Products.price as price, Products.image as image, ROUND(AVG(rating),2) as avg_review, avail_quantity
            FROM Products, ProductReviews, inv
            WHERE Products.id = ProductReviews.product_id
                AND Products.id = inv.product_id
                AND Products.description LIKE '%' || :search || '%'
                AND Products.category LIKE '%' || :category || '%'
                AND avail_quantity > :quantMin
                AND avail_quantity < :quantMax
                AND Products.price > :priceMin
                AND Products.price < :priceMax
            GROUP BY Products.id, Products.name, Products.price, Products.image, avail_quantity
            ORDER BY
                CASE WHEN :sortBy = 'default' THEN id END ASC,
                CASE WHEN :sortBy = 'highToLow' THEN price END DESC,
                CASE WHEN :sortBy = 'lowToHigh' THEN price END ASC,
                CASE WHEN :sortBy = 'avgRev' THEN AVG(rating) END DESC,
                CASE WHEN :sortBy = 'availQuant' THEN avail_quantity END DESC
            ''', search=search, sortBy=sortBy, category=category, quantMin=quantMin, quantMax=quantMax, priceMin=priceMin, priceMax=priceMax)
            return [ProductSummary(*row) for row in rows]