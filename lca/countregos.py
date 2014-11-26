#!/usr/bin/python

import csv
import datetime
import getpass
import psycopg2
import psycopg2.extras
import sys
import time

# Try to connect

password = getpass.getpass('DB password: ')

try:
    conn = psycopg2.connect("host='%(host)s' dbname='%(db)s' user='%(user)s' "
                            "password='%(password)s'"
                            % {'host': sys.argv[1],
                               'db': sys.argv[2],
                               'user': sys.argv[3],
                               'password': password})
except Exception as ex:
    print 'DB connection failed: %s' % ex
    sys.exit(1)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Find paid invoices
paid_invoices = []
payment_dates = {}

cur.execute('select * from payment_received')
rows = cur.fetchall()
for row in rows:
    if row['approved']:
        paid_invoices.append(row['invoice_id'])
        paid_dt = row['creation_timestamp']
        paid_d = datetime.datetime(paid_dt.year, paid_dt.month, paid_dt.day)
        payment_dates[row['invoice_id']] = paid_d

# Find what those invoices paid for
products_by_date = {}

cur.execute('select * from invoice_item')
rows = cur.fetchall()
for row in rows:
    invoice_id = row['invoice_id']
    if invoice_id in paid_invoices:
        products_by_date.setdefault(payment_dates[invoice_id], {})
        products_by_date[payment_dates[invoice_id]].setdefault(
            row['product_id'], 0)
        products_by_date[payment_dates[invoice_id]][row['product_id']] += 1

# Find the product category that is tickets
ticket_category = None

cur.execute('select * from product_category')
rows = cur.fetchall()
for row in rows:
    if row['name'] == 'Ticket':
        ticket_category = row['id']

if not ticket_category:
    print 'Could not find a ticket category!'
    sys.exit(1)

# Find the product ids which match that category
ticket_products = []
columns = ['date']

cur.execute('select * from product')
rows = cur.fetchall()
for row in rows:
    if row['category_id'] == ticket_category:
        ticket_products.append(row['id'])
        columns.append(row['description'])
        
# Dumpy dumpy
first_day = sorted(products_by_date.keys())[0]
last_day = sorted(products_by_date.keys())[-1]

# Special case for the current conference
recentish = datetime.datetime.now() - last_day
if recentish.days < 7:
    now = datetime.datetime.now()
    last_day = datetime.datetime(now.year, now.month, now.day)

c = csv.writer(sys.stdout, delimiter=',')
c.writerows([columns])

dt = first_day
while dt <= last_day:
    sales = ['%04d%02d%02d' %(dt.year, dt.month, dt.day)]
    for ticket_product in ticket_products:
        sales.append(products_by_date.get(dt, {}).get(ticket_product, 0))
    c.writerows([sales])

    dt += datetime.timedelta(days=1)

