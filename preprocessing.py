import os
import csv
import numpy as np
import pandas as pd

# Path configuration
os.chdir('./Data/')

orders = []
with open('orders.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count > 4021:
            break
        if line_count == 0:
            line_count += 1
        elif line_count == 1:
            orders = row
            line_count += 1
        else:
            orders = np.vstack([orders, row])
            line_count += 1

train = (orders[:, 2] == 'train').tolist()
test = (orders[:, 2] == 'test').tolist()
test_col = [a or b for a, b in zip(train, test)]
train_col = (orders[:, 2] == 'prior').tolist()

train = orders[train_col]
test = orders[test_col]

train = np.delete(train, [2, 4, 5], 1)
test = np.delete(test, [2, 4, 5], 1)

train[train == ''] = 0.0
train = train.astype(float).astype(int)
test = test.astype(float).astype(int)


train = pd.DataFrame(data=train, columns=['order_id', 'user_id', 'order_number', 'days_since_prior_order'])
train = train.astype(int)

user_id = train.user_id.unique()
for u in user_id:
        order_number = train[(train.user_id == u)].order_number
        same_day = 0
        for o in order_number[1:]:
            if train[(train.user_id == u) & (train.order_number == o)].days_since_prior_order.unique()[0] == 0:
                same_day += 1
            train.at[(train.user_id == u) & (train.order_number == o), 'order_number'] = o - same_day


test = pd.DataFrame(data=test, columns=['order_id', 'user_id', 'order_number', 'days_since_prior_order'])

product_train = pd.read_csv('order_products__prior.csv', sep=',')
product_test = pd.read_csv('order_products__train.csv', sep=',')

product_train = product_train.drop('add_to_cart_order', axis=1)
product_test = product_test.drop('add_to_cart_order', axis=1)

product_train = product_train.apply(pd.to_numeric)
product_test = product_test.apply(pd.to_numeric)

train = pd.merge(train, product_train, how='inner', on=['order_id'])
test = pd.merge(test, product_test, how='inner', on=['order_id'])

train.to_csv('./train_middle.csv', sep='\t', encoding='utf-8', index=False)
test.to_csv('./test.csv', sep='\t', encoding='utf-8', index=False)
