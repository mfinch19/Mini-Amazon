/*
\COPY Users FROM 'data/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Buyers FROM 'data/Buyers.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sellers FROM 'data/Sellers.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Category FROM 'data/Category.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Products FROM 'data/Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Purchases FROM 'data/Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'data/Cart.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellsItem FROM 'data/SellsItem.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductReview FROM 'data/ProductReview.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellerReview FROM 'data/SellerReview.csv' WITH DELIMITER ',' NULL '' CSV
*/

\COPY Users FROM 'generated/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Category FROM 'generated/Category.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Products FROM 'generated/Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Purchases FROM 'generated/Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'generated/Cart.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellsItem FROM 'generated/SellsItem.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductReview FROM 'generated/ProductReview.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellerReview FROM 'generated/SellerReview.csv' WITH DELIMITER ',' NULL '' CSV
