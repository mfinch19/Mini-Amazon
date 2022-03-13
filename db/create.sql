--- Users Guru
-- Users
CREATE TABLE Users (
	id INT PRIMARY KEY,
	email VARCHAR UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(255) NOT NULL,
	lastname VARCHAR(255) NOT NULL,
	balance DECIMAL(10,2) NOT NULL,
	zip INT NOT NULL,
	street VARCHAR(255) NOT NULL
);
-- Sellers
-- CREATE TABLE Sellers (
-- 	id INT NOT NULL PRIMARY KEY REFERENCES Users(id)
-- );
-- -- Buyers
-- CREATE TABLE Buyers (
-- 	id INT NOT NULL PRIMARY KEY REFERENCES Users(id)
-- );
--- Products Guru
-- Categories of Products
CREATE TABLE Category (
	cat_name VARCHAR(256) NOT NULL PRIMARY KEY,
	description VARCHAR(256) NOT NULL
);
-- Products
CREATE TABLE Products (
	id INT NOT NULL PRIMARY KEY,
	name VARCHAR(256) NOT NULL,
	cat_name VARCHAR(256) NOT NULL REFERENCES Category(cat_name),
	description VARCHAR(1024) NOT NULL,
	image_file VARCHAR(256) NOT NULL,
	available BOOLEAN DEFAULT TRUE
);
-- Purchases of Products
CREATE TABLE Purchases (
	order_id INT NOT NULL PRIMARY KEY,
	product_id INT NOT NULL REFERENCES Products(id),
	buyer_id INT NOT NULL REFERENCES Users(id),
	seller_id INT NOT NULL REFERENCES Users(id),
	payment_amount DECIMAL(10, 2) NOT NULL,
	quantity INT NOT NULL CHECK(quantity >= 0),
	time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	time_processed timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	status VARCHAR(12) CHECK (status IN ('Complete', 'Incomplete'))
);
--- Carts Guru
-- Cart
CREATE TABLE Cart (
	user_id INT NOT NULL REFERENCES Users(id),
	seller_id INT NOT NULL REFERENCES Users(id),
	product_id INT NOT NULL REFERENCES Products(id),
	quantity INT NOT NULL CHECK(quantity >= 0),
	price_per_item DECIMAL(10, 2) NOT NULL CHECK(price_per_item >= 0),
	PRIMARY KEY(user_id, seller_id, product_id)
);

--- Sellers Guru
-- For Sale
CREATE TABLE SellsItem (
	seller_id INT NOT NULL REFERENCES Users(id),
	product_id INT NOT NULL REFERENCES Products(id),
	price DECIMAL(10, 2) NOT NULL CHECK(price >= 0),
	stock INT NOT NULL CHECK(stock >= 0),
	PRIMARY KEY(seller_id, product_id)
);

-- History of orders fulfilled or to be fulfilled?

--- Social Guru
-- Reviews of Products
CREATE TABLE ProductReview (
	user_id INT NOT NULL REFERENCES Users(id),
	product_id INT NOT NULL REFERENCES Products(id),
	date_time DATE NOT NULL,
	description VARCHAR(256) NOT NULL,
	rating DECIMAL(10, 2) NOT NULL CHECK(rating >= 1 AND rating <= 5),
	PRIMARY KEY (user_id, product_id)
	-- FOREIGN KEY (user_id, product_id) REFERENCES Purchases(buyer_id, product_id)
);
-- Reviews of Sellers
CREATE TABLE SellerReview (
	user_id INT NOT NULL REFERENCES Users(id),
	seller_id INT NOT NULL REFERENCES Users(id),
	date_time DATE NOT NULL,
	description VARCHAR(256) NOT NULL,
	rating DECIMAL(10, 2) NOT NULL CHECK(rating >= 1 AND rating <= 5),
	PRIMARY KEY (user_id, seller_id)
	-- FOREIGN KEY (user_id, seller_id) REFERENCES Purchases(buyer_id, seller_id)
);

-- View of product summary statistics
CREATE VIEW ProductSummary AS
WITH
sells_summary AS (SELECT product_id, COUNT(*) AS sellers, AVG(price) AS avg_price, SUM(stock) AS total_stock
									FROM SellsItem
									GROUP BY product_id),
review_summary AS (SELECT product_id, COUNT(*) AS reviews, AVG(rating) AS avg_rating
									 FROM ProductReview
									 GROUP BY product_id)
SELECT p.id AS product_id, p.name, p.cat_name, p.description, p.image_file, COALESCE(s.sellers, 0) AS sellers, s.avg_price,
COALESCE(s.total_stock, 0) AS total_stock, COALESCE(r.reviews, 0) AS reviews, r.avg_rating
FROM Products p
FULL OUTER JOIN sells_summary s ON p.id = s.product_id
FULL OUTER JOIN review_summary r ON p.id = r.product_id;

-- View of seller summary statistics
CREATE VIEW SellerSummary AS
WITH
sells_summary AS (SELECT seller_id, COUNT(*) AS products, AVG(price) AS avg_price, SUM(stock) AS total_stock
									FROM SellsItem
									GROUP BY seller_id),
review_summary AS (SELECT seller_id, COUNT(*) AS reviews, AVG(rating) AS avg_rating
									 FROM SellerReview
									 GROUP BY seller_id),
purchase_summary AS (SELECT seller_id, SUM(quantity) AS items_sold, MAX(time_purchased) AS last_sold
										 FROM Purchases
									   GROUP BY seller_id)
SELECT u.id AS seller_id, u.firstname, u.lastname, COALESCE(s.products, 0) AS products, s.avg_price,
COALESCE(s.total_stock, 0) AS total_stock, COALESCE(r.reviews, 0) AS reviews, r.avg_rating,
COALESCE(p.items_sold, 0) AS items_sold, p.last_sold
FROM Users u
-- WHERE u.is_seller = 1
FULL OUTER JOIN sells_summary s ON u.id = s.seller_id
FULL OUTER JOIN review_summary r ON u.id = r.seller_id
FULL OUTER JOIN purchase_summary p ON u.id = p.seller_id;
