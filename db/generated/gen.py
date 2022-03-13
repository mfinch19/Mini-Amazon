from werkzeug.security import generate_password_hash
import csv
import random
from faker import Faker
from datetime import datetime, timedelta


num_users = 2000
num_category = 10
num_products = 1000
num_purchases = 30000
num_cart = 16000
num_item_sold = 5000
num_product_review = 25000
num_seller_review = 25000
max_stock_unit = 1000
max_purchase_unit = 50
status_list = ['Complete', 'Incomplete']
purchase_user_ID = []
purchase_seller_ID= []
purchase_product_ID = []
sells_seller_ID = []
sells_product_ID = []
sells_price = []


Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

# generate users 
def gen_users(num_users):
    email_list = []
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            while email in email_list:
                profile = fake.profile()
                email = profile['mail']
            email_list.append(email)
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            balance = random.random()*10000
            street = fake.address()
            zip = street[-5:]
            writer.writerow([uid, email, password, firstname, lastname, balance, zip, street])
        print(f'{num_users} generated')
    return

# generate categories
def gen_category(num_category):
    available_category = ['Clothing', 'Books', 'Electronics', 'Home', 'Pet Supplies', 'Beauty', 'Health', 'Sports', 'Outdoors', 'Food']
    with open('Category.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Category...', end=' ', flush=True)
        for num in range(len(available_category)):
            name = available_category[num]

            description = fake.sentence(nb_words=10)[:-1]
            writer.writerow([name, description])
            available_category.append(name)
        print(f'{num_category} generated; {len(available_category)} available')
    return available_category

# generate products
def gen_products(num_products, available_category):
    product_name = []
    product_dict = {}
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=2)[:-1]
            while name in product_name:
                name = fake.sentence(nb_words=2)[:-1]
            cat_name = fake.random_element(elements=available_category)
            product_description = fake.sentence(nb_words=10)[:-1];
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = fake.random_element(elements=('true', 'false'))
            img = 'https://picsum.photos/seed/' + 'WAMYJ' + str(pid) + '/300/300'
            if name not in product_name:
                product_dict[pid] = price
                product_name.append(name)
                writer.writerow([pid, name, cat_name, product_description, img, available])
        print(f'{num_products} generated; {len(product_dict)} available')
    return product_dict

# generate purchases
def gen_purchases(num_purchases):
    id_max = len(sells_seller_ID)

    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            product_number = fake.random_int(min=0, max=id_max-1)

            sid = sells_seller_ID[product_number]
            pid = sells_product_ID[product_number]
            purchase_user_ID.append(uid)
            purchase_seller_ID.append(sid)
            purchase_product_ID.append(pid)
            time_purchased = fake.date_time()
            time_processed = time_purchased + timedelta(weeks = 2) # Assumed all purchases are processes in a week
            if time_processed > datetime.now(tz=None): 
                status = 'Incomplete'
                time_processed = datetime(1, 1, 1, 1, 1, 1)
            else: 
                status = 'Complete'
            quantity = fake.random_int(min=1, max=30)
            payment_amount = float(sells_price[product_number]) * int(quantity)
            writer.writerow([id, pid, uid, sid, payment_amount, quantity, time_purchased, time_processed, status])
        print(f'{num_purchases} generated')
    return

# generate cart inputs
def gen_cart(num_cart):
    cart_id = []
    id_max = len(sells_seller_ID)
    with open('Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        for id in range(num_cart):
            uid = fake.random_int(min=0, max=num_users-1)
            product_number = fake.random_int(min=0, max=id_max-1)
            sid = sells_seller_ID[product_number]
            pid = sells_product_ID[product_number]
            quantity = fake.random_int(min=1, max=10)
            price = sells_price[product_number]
            key = [uid, sid, pid]
            if key not in cart_id:
                cart_id.append(key)
                writer.writerow([uid, sid, pid, quantity, price])
        print(f'{num_cart} generated')
    return

# generate items sold by users
def gen_SellsIten(num_item_sold, product_dict):
    sold_item_id = []
    with open('SellsItem.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellsItem...', end=' ', flush=True)
        for id in range(num_item_sold):
            sid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=product_dict.keys())
            price = round(float(product_dict.get(pid))*(random.random() + 0.5),2)
            stock = fake.random_int(min=0, max=max_stock_unit)
            key = [sid, pid]
            if key not in sold_item_id:
                sells_seller_ID.append(sid)
                sells_product_ID.append(pid)
                sells_price.append(price)
                sold_item_id.append(key)
                writer.writerow([sid, pid, price, stock])
        print(f'{num_item_sold} generated')
    return

# generate product reviews 
def gen_ProductReview(num_product_review):
    key_list = []
    with open('ProductReview.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('ProductReview...', end=' ', flush=True)
        for i in range(num_product_review):
            purchase_record = fake.random_int(min=0, max= len(purchase_user_ID)-1)
            uid = purchase_user_ID[purchase_record]
            pid = purchase_product_ID[purchase_record]
            time = fake.date_time()
            description = fake.sentence(nb_words=10)[:-1]
            rating = fake.random_int(min=1, max=5)
            key = [uid, pid]
            if key not in key_list:
                key_list.append(key)
                writer.writerow([uid, pid, time, description,rating])
        print(f'{num_product_review} generated')
    return 

# generate seller reviews  
def gen_SellerReview(num_seller_review):
    key_list = []
    with open('SellerReview.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellerReview...', end=' ', flush=True)
        for i in range(num_seller_review):
            purchase_record = fake.random_int(min=0, max= len(purchase_user_ID)-1)
            uid = purchase_user_ID[purchase_record]
            sid = purchase_seller_ID[purchase_record]
            time = fake.date_time()
            description = fake.sentence(nb_words=10)[:-1]
            rating = fake.random_int(min=1, max=5)
            key = [uid, sid]
            if key not in key_list:
                key_list.append(key)
                writer.writerow([uid, sid, time, description,rating])
        print(f'{num_seller_review} generated')
    return 


gen_users(num_users)
available_category = gen_category(num_category);
product_dict = gen_products(num_products, available_category)
gen_SellsIten(num_item_sold, product_dict)
gen_purchases(num_purchases)
gen_cart(num_cart)
gen_ProductReview(num_product_review)
gen_SellerReview(num_seller_review)
