import re
import sys
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Markup, session
from calendar import day_name
from datetime import date
from random import randint
from os import getcwd, path, listdir
from hashlib import md5

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CURRENT_DAY = day_name[date.today().weekday()]

path_to_data = getcwd() + "\\food.txt"
path_to_db = getcwd() + "\\creds.db"

food_dict = dict()
food_cart_dict = dict()
food_menu_of_the_day_dict = dict()

total_quantity_and_price_list = list()

app = Flask(__name__)
app.secret_key = "password"

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('username', None)
        session.pop('is_admin', None)
        session.pop('discount', None)

    return redirect(url_for('login'))

@app.route('/authenticate', methods = ['GET', 'POST'])
def authenticate():
    post_parameters = request.form
    
    username = post_parameters.get("username").lower().strip()
    password = post_parameters.get("password")

    regex = r"^[a-z]*$"
    passed_regex = re.match(regex, username)

    if passed_regex and username != "" and password != "":
        hashed_password = md5(password.encode()).hexdigest()

        authentication_results = authenticate_user(username, hashed_password)

        if len(authentication_results) > 0:
            # [('admin', '21232f297a57a5a743894a0e4a801fc3', 'yes', '15')]
            # Is a tuple contained in a list.
            # list[0] -> authentication data   
            authentication_results = authentication_results[0]     

            session['username'] = authentication_results[0]
            session['discount'] = authentication_results[3]

            if authentication_results[2] == "yes":
                session['is_admin'] = "yes"

            if 'is_admin' in session:
                return redirect(url_for('home_admin'))

            else:
                return redirect(url_for('home_user'))   

        else:
            message = "Either username or password is wrong."

            return render_template('login.html', message = message) 

    else:
        message = "Username must contain only alphabets.<br>"
        message += "Username and Password must not be empty.<br>"
        message = Markup(message)
        
        return render_template('login.html', message = message) 

@app.errorhandler(404)
def page_not_found(error_code):
    # Error page.
    return render_template('404.html'), 404

@app.route('/user')
def home_user():
    return render_template('index.html', weekdays = WEEKDAYS, current_day = CURRENT_DAY)

@app.route('/user/view/<day_of_the_week>')
def view(day_of_the_week):
    food_menu_dict = food_dict.get(day_of_the_week)

    # food_menu will be None if key(day_of_the_week) is non-existent.
    if food_menu_dict: # True.
        return render_template('data.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY)
    else:
        return render_template('404.html')

@app.route('/admin')
def home_admin():
    if 'is_admin' in session: 
        return render_template('index_admin.html', weekdays = WEEKDAYS, username = session['username'])    
    else:
        return redirect(url_for('login'))   

@app.route('/admin/edit/<day_of_the_week>')
def edit(day_of_the_week):
    if 'is_admin' in session: 
        food_menu_dict = food_dict.get(day_of_the_week)

        if food_menu_dict:
            return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY)
        else:
            return render_template('404.html')

    else:
        return redirect(url_for('login'))

@app.route('/admin/save', methods = ['GET', 'POST'])
def save_changes():
    if request.method == 'POST':
        if 'is_admin' in session:
            global food_dict
            global food_cart_dict
            global total_quantity_and_price_list

            temp_food_dict = dict()

            food_cart_dict.clear()
            total_quantity_and_price_list.clear()

            message = ""
            updated = False
            post_parameters = request.form      

            day_of_the_week = post_parameters.get("day_of_the_week")
            old_food_name = post_parameters.get("old_food_name")
            old_food_price = post_parameters.get("old_food_price")

            new_food_name = post_parameters.get("new_food_name").strip()
            new_food_price = post_parameters.get("new_food_price").strip()

            temp_food_dict = food_dict.get(day_of_the_week)

            if old_food_name != "" and old_food_price != "":
                if new_food_name != "" and new_food_price != "":
                    # Only accepts alphabets and spaces.
                    regex = r"^[A-Za-z ]*$"
                    regex_passed = re.match(regex, new_food_name)
                    
                    if regex_passed:
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
                                # Check for duplicate.
                                if new_food_name in temp_food_dict:
                                    message += f"There is already \"{new_food_name}\" in the existing menu."

                                else:
                                    new_food_price = float(new_food_price)

                                    if new_food_price > 0:
                                        # Delete old food name, old price remains, key name changed.
                                        temp_food_dict[new_food_name] = temp_food_dict.pop(old_food_name) 

                                        # Update the changed key name with new price.
                                        temp_food_dict[new_food_name] = new_food_price 

                                        # Update global nested dictionary.
                                        food_dict[day_of_the_week] = temp_food_dict

                                        # Update data file with new changes from nested dictionary.
                                        update_file(path_to_data, food_dict)
                                        updated = True

                                    else:
                                        message += "New food price must not be lesser than 0."
                            
                            except ValueError:
                                message += "New food price must be in floating point format."
                    
                    else:
                        message += "Only alphabets and spaces are accepted for New food"

                else:
                    message += "New food name and/or food price must not be empty."

            else:
                message += "Press Edit to populate Old Food Name and Old Food price."
            
            food_menu_dict = food_dict.get(day_of_the_week)

            if updated:
                refresh_data()
                message = "Successfully updated data!"

                return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY, message = message)
            
            else:
                return render_template('edit.html', food_menu_dict = food_menu_dict, day_of_the_week = day_of_the_week, current_day = CURRENT_DAY, message = message)

        else:
            return redirect(url_for('login'))

    else:
        return redirect(url_for('home_admin'))

@app.route('/download', methods = ['GET', 'POST'])
def download_file():
    post_parameters = request.form

    if len(post_parameters) > 0:
        for filename in post_parameters:
            file_to_be_downloaded = filename 

        path_to_download_folder = getcwd() + "\\download\\" 
        
        return send_from_directory(path_to_download_folder, file_to_be_downloaded, as_attachment = True)
    
    else:
        files_in_directory = listdir(getcwd() + "\\download")
        number_of_files = len(files_in_directory)

        return render_template('download.html', files_in_directory = files_in_directory, number_of_files = number_of_files)

# 1st -> order_food.html
@app.route('/order/form')
def form():
    refresh_data()
    return render_template('order_food.html', food_data = food_menu_of_the_day_dict, current_day = CURRENT_DAY)

# 2nd -> Form action submitted to /order/cart
@app.route('/order/cart', methods = ['GET', 'POST'])  
def order_food():
    global food_cart_dict
    global total_quantity_and_price_list

    food_cart_dict.clear()
    total_quantity_and_price_list.clear()

    order_number = randint(1, 500)

    post_parameters = request.form

    total_price = 0
    total_quantity = 0

    for food_name in post_parameters:
        try:
            food_quantity = int(post_parameters.get(food_name))

            if food_quantity > 0:
                food_price = food_menu_of_the_day_dict.get(food_name)
                food_price *= food_quantity

                total_quantity += food_quantity
                total_price += food_price

                price_and_quantity_list = [food_price, food_quantity]
                food_cart_dict[food_name] = price_and_quantity_list
        
        # If quantity is empty. Conversion to int will fail. If that happens, do nothing.
        except ValueError:
            pass

    total_quantity_and_price_list = [total_quantity, total_price]

    if len(food_cart_dict) > 0:
        return redirect(url_for('cart', order_number = order_number))

    else:
        refresh_data()
        return render_template('order_food.html', food_data = food_menu_of_the_day_dict, current_day = CURRENT_DAY)
   
# 3rd -> Redirected to order number
@app.route('/order/<order_number>') 
def cart(order_number):
    return render_template('cart.html', order_number = order_number, food_cart_dict = food_cart_dict, total_quantity_and_price_list = total_quantity_and_price_list)

@app.route('/order/save', methods = ['GET', 'POST'])
def save_order():
    post_parameters = request.form

    # Only interested in order number.
    for order in post_parameters:
        order_number = order

    print_receipt(order_number)

    return render_template('order_saved.html', order_number = order_number)

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

                if food_day == day_of_the_week:
                    food_name_and_price_dict[food_name] = float(food_price)

            temp_food_dict[day_of_the_week] = food_name_and_price_dict

        return temp_food_dict

    else:
        # Exit program if we are not able to read from our data file.
        print(f"Could not open -> {path_to_data}")
        sys.exit(1)

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

        f.write(data.strip())

def print_receipt(order_number):
    if len(food_cart_dict) > 0 and len(total_quantity_and_price_list) > 0:
        path_to_receipt = getcwd() + f"\\download\\{order_number}.txt"

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

def refresh_data():
    global food_dict
    global food_menu_of_the_day_dict

    # To update the global nested dictionary and menu of the day data with new changes.
    food_dict = load_data_to_nested_dict()
    food_menu_of_the_day_dict = food_dict.get(CURRENT_DAY)

def authenticate_user(username, password):
    db_file_exist = path.exists(path_to_db)

    if db_file_exist:
        try:
            sqlite_connection = sqlite3.connect(path_to_db)
            cursor = sqlite_connection.cursor()

            query = f"SELECT username, password, is_admin, discount FROM credentials WHERE "
            query += f"username = \"{username}\" and password = \"{password}\" LIMIT 1"

            cursor.execute(query)
            result = cursor.fetchall()

            return result
        
        except sqlite3.Error as error:
            print(f"Error -> {error}")
            sys.exit(1)

        finally:
            if sqlite_connection:
                sqlite_connection.close()
    
    else:
        print(f"Unable to find DB file.")
        sys.exit(1)

if __name__ == '__main__':
    refresh_data()
    app.run()