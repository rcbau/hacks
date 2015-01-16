#!/usr/bin/python

import csv
import datetime
import getpass
import psycopg2
import psycopg2.extras
import sys
import time

DEBUG = False

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

# Determine item prices
product_prices = {}
product_names = {}
cur.execute('select * from product')
rows = cur.fetchall()
for row in rows:
    product_prices[row['id']] = row['cost']
    product_names[row['id']] = row['description']

# Cache invoice dates
invoice_dates = {}
cur.execute('select * from invoice where void is null')
rows = cur.fetchall()
for row in rows:
    invoice_dates[row['id']] = row['issue_date']

# Cache people
people = {}
cur.execute('select * from person')
rows = cur.fetchall()
for row in rows:
    people[row['id']] = '%s, %s' %(row['lastname'], row['firstname'])

# Cache vouchers which have been presented
presented_vouchers = {}
cur.execute('select * from registration where voucher_code <> \'\'')
rows = cur.fetchall()
for row in rows:
    presented_vouchers.setdefault(row['person_id'], [])
    presented_vouchers[row['person_id']].append(row['voucher_code'])

# Cache a mapping of invoices to people
invoice_people = {}
cur.execute('select * from invoice')
rows = cur.fetchall()
for row in rows:
    invoice_people[row['id']] = row['person_id']

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

# Invoices worth $0 are also "paid"
invoice_totals = {}

cur.execute('select * from invoice_item')
rows = cur.fetchall()
for row in rows:
    invoice_totals.setdefault(row['invoice_id'], 0)
    invoice_totals[row['invoice_id']] += row['cost']

for invoice_id in invoice_totals:
    if not invoice_id in invoice_dates:
        continue
    
    if DEBUG:
        print 'Invoice %s for %s' %(invoice_id, invoice_totals[invoice_id])

    if invoice_totals[invoice_id] == 0 and not invoice_id in paid_invoices:
        paid_invoices.append(invoice_id)
        paid_dt = invoice_dates[invoice_id]
        paid_d = datetime.datetime(paid_dt.year, paid_dt.month, paid_dt.day)
        payment_dates[invoice_id] = paid_d

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

columns.append('vouchers presented')
        
# Find what those invoices paid for
products_by_date = {}
vouchers_by_date = {}
revenue_by_date = {}

cur.execute('select * from invoice_item')
rows = cur.fetchall()
for row in rows:
    invoice_id = row['invoice_id']
    if invoice_id in paid_invoices and row['product_id'] in ticket_products:
        if DEBUG:
            print '%s bought a %s on %s' %(people[invoice_people[invoice_id]],
                                          product_names.get(row['product_id']),
                                          payment_dates[invoice_id])

        person_id = invoice_people[invoice_id]
        if person_id in presented_vouchers:
            vouchers_by_date.setdefault(payment_dates[invoice_id], [])
            vouchers_by_date[payment_dates[invoice_id]].append(
                presented_vouchers[person_id])

        products_by_date.setdefault(payment_dates[invoice_id], {})
        products_by_date[payment_dates[invoice_id]].setdefault(
            row['product_id'], 0)
        products_by_date[payment_dates[invoice_id]][row['product_id']] += 1

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
    sales.append(len(vouchers_by_date.get(dt, [])))
    c.writerows([sales])

    dt += datetime.timedelta(days=1)

