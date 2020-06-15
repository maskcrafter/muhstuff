from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Markup
from calendar import day_name
from datetime import date
from random import randint
from os import getcwd, path, listdir

import sys
import re

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CURRENT_DAY = day_name[date.today().weekday()]

path_to_data = getcwd() + "\\food.txt"

food_dict = dict()
food_cart_dict = dict()
food_menu_of_the_day_dict = dict()

total_quantity_and_price_list = list()
url_list = list()

order_raised = False

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(error_code):
    return render_template('404.html'), 404

@app.route('/')
def home():
    global url_list

    for day_of_the_week in WEEKDAYS:
        url_list.append(f"/{day_of_the_week}")

    return render_template('index.html', url_list = url_list, weekdays = WEEKDAYS, current_day = CURRENT_DAY)

@app.route('/view/<day_of_the_week>')
def view(day_of_the_week):
    food_menu_dict = food_dict.get(day_of_the_week)

    # food_menu will be None if key(day_of_the_week) is non-existent
    if food_menu_dict:  # True
        return render_template('data.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY)
    else:
        return render_template('404.html')

@app.route('/admin/<day_of_the_week>')
def edit(day_of_the_week):
    food_menu_dict = food_dict.get(day_of_the_week)

    if food_menu_dict:
        return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY)
    else:
        return render_template('404.html')

@app.route('/admin/save')
def save_changes():
    global food_dict
    global food_cart_dict
    global total_quantity_and_price_list

    temp_food_dict = dict()

    food_cart_dict.clear()
    total_quantity_and_price_list.clear()

    get_parameters = request.args

    day_of_the_week = get_parameters.get("day_of_the_week")
    
    old_food_name = get_parameters.get("old_food_name")
    old_food_price = get_parameters.get("old_food_price")

    new_food_name = get_parameters.get("new_food_name").strip()
    new_food_price = get_parameters.get("new_food_price").strip()

    temp_food_dict = food_dict.get(day_of_the_week)

    updated = False
    message = ""

    # New food name and new food price is not empty.
    if new_food_name != "" and new_food_price != "":
        # Only accepts alphabets and spaces.
        regex = r"^[A-Za-z ]*$"
        
        # Regex passed.
        if re.match(regex, new_food_name):

            # Change only Key values.
            if new_food_name == old_food_name:
                try:
                    old_food_price = float(old_food_price)
                    new_food_price = float(new_food_price)

                    if new_food_price == old_food_price:
                        message += "New food name and prices are the same.<br>"
                        message += "As such, no changes will be made."
                        message = Markup(message)

                    elif new_food_price > 0:
                        # Key name remains the same, only values changed.
                        temp_food_dict[old_food_name] = new_food_price
                        food_dict[day_of_the_week] = temp_food_dict
                        
                        update_file(path_to_data, food_dict)
                        updated = True

                    else:
                        message += "New food price must not be lesser than 0."

                except ValueError:
                    message += "New food price must be in floating point format."

            # If new food name is different from old food name.
            else:
                try:
                    new_food_price = float(new_food_price)

                    if new_food_price > 0:
                        temp_food_dict[new_food_name] = temp_food_dict.pop(old_food_name)
                        temp_food_dict[new_food_name] = new_food_price
                        food_dict[day_of_the_week] = temp_food_dict

                        update_file(path_to_data, food_dict)
                        updated = True

                    else:
                        message += "New food price must not be lesser than 0."
                
                except ValueError:
                    message += "New food price must be in floating point format."
        
        # Failed regex. 
        else:
            message += "Only alphabets and spaces are accepted for New food"

    # New food name and/or new food price is empty.
    else:
        message += "New food name and/or food price must not be empty."

    food_menu_dict = food_dict.get(day_of_the_week)

    if updated:
        refresh_data()
        message = "Successfully updated data!"

        return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY, message = message)
    
    else:
        return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY, message = message)

# 1st -> order_food.html
@app.route('/order/form')    
def form():
    refresh_data()
    return render_template('order_food.html', food_data = food_menu_of_the_day_dict, current_day = CURRENT_DAY)

# 2nd -> Form action submitted to /order/cart
@app.route('/order/cart')  
def order_food():
    global food_cart_dict
    global total_quantity_and_price_list
    global order_raised

    food_cart_dict.clear()
    total_quantity_and_price_list.clear()

    order_number = randint(1, 500)
    get_parameters = request.args

    total_price = 0
    total_quantity = 0

    # Example of get_paramters:
    # Chicken Congee : '' -> No value(Not selected by user).
    # Chicken Rice : '1' -> Value exist but in string format.
    for food_name in get_parameters:
        try:
            food_quantity = int(get_parameters.get(food_name))

            if food_quantity > 0:
                food_price = food_menu_of_the_day_dict.get(food_name)
                food_price *= food_quantity # Get the price of a particular food if a quantity is given.

                total_quantity += food_quantity
                total_price += food_price
                    
                price_and_quantity_list = [food_price, food_quantity]
                food_cart_dict[food_name] = price_and_quantity_list
        
        # ValueError happens when quantity field is blank. Will do nothing and goes to the next loop.
        except ValueError:
            pass           

    total_quantity_and_price_list = [total_quantity, total_price]

    if len(food_cart_dict) > 0:
        order_raised = True
        return redirect(url_for('cart', order_number = order_number))
    else:
        refresh_data()
        return render_template('order_food.html', food_data = food_menu_of_the_day_dict, current_day = CURRENT_DAY)
   
# 3rd -> Redirected to order number
@app.route('/order/<order_number>') 
def cart(order_number):
    global order_raised

    if order_raised:
        order_raised = False
        return render_template('cart.html', order_number = order_number, food_cart_dict = food_cart_dict, total_quantity_and_price_list = total_quantity_and_price_list)
    else:
        return render_template('404.html')

@app.route('/download')
def download_file():
    get_parameters = request.args

    if len(get_parameters) > 0:
    # Only interested in order number and nothing else.
        for number in get_parameters:
            order_number = number 

        receipt = f"{order_number}.txt"
        path_to_download_folder = getcwd() + "\\download\\" 
        
        return send_from_directory(path_to_download_folder, receipt, as_attachment = True)
    
    else:
        non_filtered_files = listdir(getcwd() + "\\download")
        num_of_files = len(non_filtered_files)

        regex = r"\.txt"

        filtered_files = list()
        for file in non_filtered_files:
            filtered_files.append(re.sub(regex, '', file))

        return render_template('download.html', files = filtered_files, num_of_files = num_of_files)

@app.route('/order/save')
def save_order():
    get_parameters = request.args

    # Only interested in order number and nothing else.
    for number in get_parameters:
        order_number = number

    path_to_receipt = f"/download/{order_number}.txt"
    print_receipt(order_number)

    return render_template('order_saved.html', order_number = order_number, path_to_receipt = path_to_receipt)

def print_receipt(order_number):
    # This if condition means that if there is an order, save the order to a file.
    if len(food_cart_dict) > 0 and len(total_quantity_and_price_list) > 0:
        path_to_receipt = getcwd() + f"\\download\{order_number}.txt"

        with open(path_to_receipt, 'w') as f:
            data = "Thank you for ordering from SPAM.\n"
            data += f"Order number: #{order_number}\n\n"
            data += "=" * 64
            data += "\nYour order\n"
            data += "=" * 64

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict.get(food_name)

                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                data += f"\n{count}. {food_name_and_quantity.ljust(50)} ${food_price:.2f}"

            total_price = total_quantity_and_price_list[1]
            total_price = f"${total_price:.2f}".rjust(55)

            data += "\n"
            data += "=" * 64
            data += f"\nTotal{total_price}\n"
            data += "=" * 64
            data += "\n\nPlease present this receipt at the counter.\n"
            data += f"Total amount payable -> {total_price.strip()}"

            f.write(data)      

def load_data_to_nested_dict():
    temp_food_dict = dict()
    file_exist = path.exists(path_to_data)

    if file_exist:
        with open(path_to_data, 'r') as f:
            data = f.readlines()
        
        # Outer dictionary -> Monday to Sunday.
        for day_of_the_week in WEEKDAYS:
            food_name_and_price_dict = dict()

            # Inner dictionary -> For particular day of the week -> food name and food price.
            for food in data:
                food_day, food_name, food_price = food.split(',')

                # For Monday, only get food name and food price for monday
                # For Tuesday, only get food name and food price for tuesday and so on.
                if food_day == day_of_the_week:
                    food_name_and_price_dict[food_name] = float(food_price)

            temp_food_dict[day_of_the_week] = food_name_and_price_dict

        return temp_food_dict
    else:
        # Exit program if we are not able to read from our data file.
        print(f"Could not open -> {path_to_data}")
        sys.exit(1)

def refresh_data():
    # This function loads the latest data into both:
    # 1. nested dictionary
    # 2. menu of the day
    global food_dict
    global food_menu_of_the_day_dict

    food_dict = load_data_to_nested_dict()
    food_menu_of_the_day_dict = food_dict.get(CURRENT_DAY)

def update_file(filename, food_dict):
    with open(filename, 'w+') as f:
        data = ""

        # Outer loop -> Monday to Sunday.
        for day_of_the_week in food_dict:
            day_of_the_week_food_dict = food_dict.get(day_of_the_week)

            # Inner loop -> Food for a particular day.
            for food_name in day_of_the_week_food_dict:
                food_price = day_of_the_week_food_dict.get(food_name)
                data += f'{day_of_the_week},{food_name},{food_price}\n'

        # Removes extra newlines from previous execution.
        f.write(data.strip())

if __name__ == '__main__':
    refresh_data()
    app.run(debug = True)