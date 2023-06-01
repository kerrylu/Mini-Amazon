\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);
\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Tags FROM 'Tags.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
\COPY CartEntries FROM 'CartEntries.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                         (SELECT MAX(id)+1 FROM Orders),
                         false);
\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellerReviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV