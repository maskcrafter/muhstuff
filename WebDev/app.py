from flask import Flask, render_template, request, redirect, url_for
from calendar import day_name
from datetime import date
from random import randint

import os
import sys

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CURRENT_DAY = day_name[date.today().weekday()]

food_dict = dict()
food_cart_dict = dict()
food_menu_of_the_day_dict = dict()

app = Flask(__name__)

@app.route('/')
def home():
    url_list = list()

    for day_of_the_week in WEEKDAYS:
        url_list.append(f"http://localhost/{day_of_the_week}")

    return render_template('index.html', url_list = url_list, weekdays = WEEKDAYS)

@app.route('/view/<day_of_the_week>')
def view(day_of_the_week):
    food_menu_dict = food_dict.get(day_of_the_week)

    # food_menu will be None if key(day_of_the_week) is non-existent
    if food_menu_dict:  # True
        return render_template('data.html', food_data = food_menu_dict, day_of_the_week = day_of_the_week)
    else:
        return render_template('404.html', message = f'/view/{day_of_the_week} was not found.')

@app.route('/order/form')   # 1st -> order_food.html 
def form():
    refresh_data()
    return render_template('order_food.html', food_data = food_menu_of_the_day_dict, current_day = CURRENT_DAY)

@app.route('/order/cart')   # 2nd -> Form action submitted to /order/cart
def order_food():
    global food_cart_dict
    food_cart_dict.clear()

    order_number = randint(1, 500)
    get_parameters = request.args

    for food_name in get_parameters:
        try:
            food_quantity = int(get_parameters.get(food_name))

            if food_quantity > 0:
                food_price = food_menu_of_the_day_dict.get(food_name)
                price_and_quantity_list = [food_price, food_quantity]
                food_cart_dict[food_name] = price_and_quantity_list
        
        # ValueError happens when quantity field is blank. Will do nothing and goes to the next loop.
        except ValueError:
            pass           

    return redirect(url_for('cart', order_number = order_number))

@app.route('/order/<order_number>') # 3rd -> Redirected to order number
def cart(order_number):
    return render_template('cart.html', order_number = order_number, food_cart_dict = food_cart_dict)

def load_data_to_nested_dict():
    temp_food_dict = dict()

    current_path = os.getcwd()
    path_to_data = current_path + "\\food.txt"
    file_exist = os.path.exists(path_to_data)

    if file_exist:
        with open(path_to_data, 'r') as f:
            data = f.readlines()
        
        for day_of_the_week in WEEKDAYS:
            food_name_and_price_dict = dict()

            for food in data:
                food_day, food_name, food_price = food.split(',')

                if food_day == day_of_the_week:
                    food_name_and_price_dict[food_name] = float(food_price)

            temp_food_dict[day_of_the_week] = food_name_and_price_dict

        return temp_food_dict

    else:
        print(f"Could not open -> {path_to_data}")
        sys.exit(1)

def refresh_data():
    global food_dict
    global food_menu_of_the_day_dict

    food_dict = load_data_to_nested_dict()
    food_menu_of_the_day_dict = food_dict.get(CURRENT_DAY)

if __name__ == '__main__':
    refresh_data()
    app.run(debug = True)
