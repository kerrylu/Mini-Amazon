from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import datetime as DT

num_users = 100
num_sellers = int(num_users/4)
num_products = 2000
num_orders = 2500
endTime = DT.datetime(2038, 1, 19, 3, 14, 7)

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    addresses = {}
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = fake.address()
            balance = f'{str(fake.random_int(max=1000))}.{fake.random_int(max=99):02}'
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
            addresses[uid] = address
        print(f'{num_users} generated')
    return addresses


def gen_products(num_products):
    prices = {}
    categories = ["Clothing", "Books", "Electronics", "Home", "Outdoors", "Food"]
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.sentence(nb_words=14)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            category = categories[fake.random_int(min=0,max=5)]
            image_path = "https://picsum.photos/seed/" + str(pid + 1) + "/200/200"
            writer.writerow([pid, name, category, description, price,  image_path])
            prices[pid] = price
        print(f'{num_products} generated; {num_products} available')
    return prices

def gen_sellers(num_sellers):
    all_sids = []
    avail_uids = []
    for i in range(num_users):
        avail_uids.append(i)
    with open('Sellers.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        for ind in range(num_sellers):
            if ind % 5 == 0:
                print(f'{ind}', end=' ', flush=True)
            sid = fake.random_element(avail_uids)
            all_sids.append(sid)
            avail_uids.remove(sid)
            writer.writerow([sid])
        print(f'{num_sellers} generated')
    return all_sids

def gen_tags(num_tags):
    used_tags = []
    with open('Tags.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Tags...', end=' ', flush=True)
        for ind in range(num_tags):
            if ind % 100 == 0:
                print(f'{ind}', end=' ', flush=True)
            pid = fake.random_int(min=0, max=num_products-1)
            tag = fake.word()
            while (pid, tag) in used_tags:
                pid = fake.random_int(min=0, max=num_products-1)
                tag = fake.word()
            used_tags.append((pid,tag))
            writer.writerow([pid, tag])
        print(f'{num_tags} generated')
    return

def gen_invents(num_ins, all_sids):
    used_products = []
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        for ind in range(num_ins):
            if ind % 100 == 0:
                print(f'{ind}', end=' ', flush=True)
            pid = fake.random_int(min=0, max=num_products-1)
            sid = fake.random_element(all_sids)
            while (pid,sid) in used_products:
                pid = fake.random_int(min=0, max=num_products-1)
                sid = fake.random_element(all_sids)
            used_products.append((pid,sid))
            quantity = fake.random_int(0,100)
            writer.writerow([pid, sid, quantity])
        print(f'{num_ins} generated')
    return

def gen_cartEs(num_cartEs, prices, all_sids):
    used = []
    with open('CartEntries.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart Entries...', end=' ', flush=True)
        for ind in range(num_cartEs):
            if ind % 100 == 0:
                print(f'{ind}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_int(min=0, max=num_products-1)
            sid = fake.random_element(all_sids)
            while uid == sid:
                sid = fake.random_element(all_sids)
            while (uid,pid,sid) in used:
                uid = fake.random_int(min=0, max=num_users-1)
                pid = fake.random_int(min=0, max=num_products-1)
                sid = fake.random_element(all_sids)
                while uid == sid:
                    sid = fake.random_element(all_sids)
            used.append((uid,pid,sid))
            quantity = fake.random_int(1,5)
            price = prices[pid]
            saved = fake.random_element(elements=('true', 'false'))
            writer.writerow([uid, sid, pid, quantity,price,saved])
        print(f'{num_cartEs} generated')
    return

def gen_orders(num_orders, addresses, purchases):
    buys = {}
    buysppl = {}
    for uid in range(num_users):
        buys[uid] = []
        buysppl[uid] = []
    orders = []
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for oid in range(num_orders):
            if oid % 100 == 0:
                print(f'{oid}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            uadd = addresses[uid]
            order_total = 0
            orderdatetime = DT.datetime.today() + DT.timedelta(days=1)
            fuldatetime = DT.datetime.today()
            orders.append([uid,uadd,order_total,orderdatetime,fuldatetime])
        for purchase in purchases:
            curOID = purchase[0]
            orders[curOID][2] = orders[curOID][2] + float(purchase[4])
            curFulDT = orders[curOID][4]
            curOrderDT = orders[curOID][3]
            if curFulDT != endTime:
                if purchase[5] == endTime:
                    orders[curOID][4] = endTime
                else:
                    orders[curOID][4] = max(curFulDT,purchase[5])
            if purchase[5] != endTime:
                orders[curOID][3] = min(curOrderDT,purchase[5])
            uid = orders[curOID][0]
            buys[uid].append((purchase[2],purchase[1]))
            buysppl[uid].append(purchase[1])
        for oid in range(num_orders):
            order = orders[oid]
            uid = order[0]
            uadd = order[1]
            order_total= order[2]
            orderdatetime = order[3] - DT.timedelta(weeks=2)
            fuldatetime = endTime
            if order[4] != endTime:
                fuldatetime = order[4]
            writer.writerow([oid, uid, uadd,order_total, orderdatetime,fuldatetime])
        print(f'{num_orders} generated')
    return buys, buysppl

def gen_purchases(num_purs, prices, all_sids):
    used = []
    purchases = []
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purs):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            if id < num_orders:
                oid = id
            else:
                oid = fake.random_int(min=0, max=num_orders-1)
            sid = fake.random_element(all_sids)
            pid = fake.random_int(min=0, max=num_products-1)
            while (oid,sid,pid) in used:
                oid = fake.random_int(min=0, max=num_orders-1)
                sid = fake.random_element(all_sids)
                pid = fake.random_int(min=0, max=num_products-1)
            used.append((oid,sid,pid))
            quantity = fake.random_int(1,5)
            price = prices[pid]
            time = fake.date_time_this_decade()
            time_fulfilled = endTime
            if time < DT.datetime.today() - DT.timedelta(weeks=24):
                time_fulfilled = time
            writer.writerow([oid, sid, pid, quantity, price, time_fulfilled])
            purchases.append((oid, sid, pid, quantity, price, time_fulfilled))
        print(f'{num_purs} generated')
    return purchases

def gen_prodRevs(num_prodrevs, all_sids, buys):
    used = []
    with open('ProductReviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product Reviews...', end=' ', flush=True)
        for ind in range(num_prodrevs):
            if ind % 100 == 0:
                print(f'{ind}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pairs = len(buys[uid])
            pair = fake.random_int(min=0, max=pairs-1)
            pid, sid = buys[uid][pair]
            while uid == sid:
                pair = fake.random_int(min=0, max=pairs-1)
                pid, sid = buys[uid][pair]
            while (uid,pid,sid) in used:
                uid = fake.random_int(min=0, max=num_users-1)
                pairs = len(buys[uid])
                while pairs == 0:
                    uid = fake.random_int(min=0, max=num_users-1)
                    pairs = len(buys[uid])
                pair = fake.random_int(min=0, max=pairs-1)
                pid, sid = buys[uid][pair]
                while uid == sid:
                    pair = fake.random_int(min=0, max=pairs-1)
                    pid, sid = buys[uid][pair]
            used.append((uid,pid,sid))
            description = fake.sentence(nb_words=40)[:-1]
            rating = fake.random_int(1,5)
            upvotes = fake.random_int(0,num_users-1)
            revdatetime = fake.date_time_this_decade()
            filename = "Test"
            writer.writerow([uid, sid, pid, description, rating, upvotes, revdatetime, filename])
        print(f'{num_prodrevs} generated')
    return

def gen_sellRevs(num_sellrevs, all_sids, buysppl):
    used = []
    with open('SellerReviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Reviews...', end=' ', flush=True)
        for ind in range(num_sellrevs):
            if ind % 100 == 0:
                print(f'{ind}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            sells = len(buysppl[uid])
            sell = fake.random_int(min=0, max=sells-1)
            sid = buysppl[uid][sell]
            while uid == sid:
                sell = fake.random_int(min=0, max=sells-1)
                sid = buysppl[uid][sell]
            while (uid,sid) in used:
                uid = fake.random_int(min=0, max=num_users-1)
                sells = len(buysppl[uid])
                sell = fake.random_int(min=0, max=sells-1)
                sid = buysppl[uid][sell]
                while uid == sid:
                    sell = fake.random_int(min=0, max=sells-1)
                    sid = buysppl[uid][sell]
            used.append((uid,sid))
            description = fake.sentence(nb_words=40)[:-1]
            rating = fake.random_int(1,5)
            upvotes = fake.random_int(0,num_users-1)
            revdatetime = fake.date_time_this_decade()
            writer.writerow([uid, sid, description, rating, upvotes, revdatetime])
        print(f'{num_sellrevs} generated')
    return

addresses = gen_users(num_users)
prices = gen_products(num_products)
all_sids = gen_sellers(num_sellers)
gen_tags(num_products*4)
gen_invents(num_products*2, all_sids)
gen_cartEs(int(2*num_users/3), prices, all_sids)
purchases = gen_purchases(num_orders*5, prices, all_sids)
buys, buysppl = gen_orders(num_orders, addresses, purchases)
print(buys[21])
gen_prodRevs(num_products*5, all_sids, buys)
gen_sellRevs(int(num_sellers*num_users/3), all_sids, buysppl)