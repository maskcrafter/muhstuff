import re
import sys
import sqlite3

from time import sleep
from os import system, getcwd, path
from calendar import day_name
from datetime import date
from random import randint
from hashlib import md5
from subprocess import Popen

# Class for manipulation of food data.
class Data:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day = day_name[date.today().weekday()]

    def __init__(self, food_file, db_file):
        self.food_file = food_file
        self.db_file = db_file

    def load_data_to_nested_dict(self, food_data):
        temp_food_dict = dict()

        # Outer Loop. Monday to Sunday.
        for day_of_the_week in self.weekdays:
            food_name_and_price_dict = dict()

            # Inner Loop. If day matches outer loop, create nested dictionary.
            for food in food_data:
                food_day, food_name, food_price = food.split(',')

                if food_day == day_of_the_week:
                    food_name_and_price_dict[food_name] = float(food_price)

            temp_food_dict[day_of_the_week] = food_name_and_price_dict

        return(temp_food_dict)

    def load_data_from_file(self):
        file_exist = path.exists(self.food_file)

        if file_exist:
            with open(self.food_file, 'r') as f:
                data = f.readlines()
        
        return(data)

    def get_todays_menu(self, food_data):
        return(food_data.get(self.current_day))

    def list_food(self, food_dict):
        for count, food_name in enumerate(food_dict, 1):
            food_price = food_dict.get(food_name)
            print(f"\t{count}. {food_name.ljust(35)} ${food_price:.2f}")

    def convert_nested_dict_into_data_and_store_it_in_file(self, filename, food_dict):
        with open(filename, 'w+') as f:
            data = ""

            # Outer loop -> Monday to Sunday.
            for day_of_the_week in food_dict:
                day_of_the_week_food_dict = food_dict.get(day_of_the_week)

                # Inner loop -> Food for a given day. 
                for food_name in day_of_the_week_food_dict:
                    food_price = day_of_the_week_food_dict.get(food_name)
                    data += f"{day_of_the_week},{food_name},{food_price}\n"
            
            f.write(data.strip())

# Class for organising food data.
class Food:
    def __init__(self, food_dict, food_cart_dict, food_of_the_day_dict, search_hits_dict):
        self.food_dict = food_dict
        self.food_cart_dict = food_cart_dict
        self.food_of_the_day_dict = food_of_the_day_dict
        self.search_hits_dict = search_hits_dict

# Class for organising login credentials
class Login:
    def __init__(self, username, password, is_admin, discount):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.discount = discount

def pause():
    print()
    system("pause")

def short_pause():
    sleep(1.2)

def clear_screen():
    system("cls")

def print_header(header_message):
    print('\t' + '=' * 64)
    print(f"{header_message}")
    print('\t' + '=' * 64)

def specify_quantity(ordered_food_name, ordered_food_price):
    clear_screen()
    print_header(f"\t{ordered_food_name}'s page.")

    instructions = "\tOnly digits are accepted."
    instructions += "\n\tMin digits - 1, Max digits - 2 ."
    instructions += "\n\n\tQuantity -> "

    try:
        order_quantity = int(input(instructions).strip())

        if order_quantity == 0:
            print(f"\n\tYou have cancelled ordering {ordered_food_name}.")
            short_pause()
            return "break"

        elif order_quantity < 0:
            print("\n\tNegative values are not accepted.")
            short_pause()

        elif order_quantity > 20:
            print("\n\tExcessive quantity are not accepted.")
            short_pause()

        else:
            price_and_quantity_list = [ordered_food_price, order_quantity]
            food_data.food_cart_dict[ordered_food_name] = price_and_quantity_list

            print(f"\n\tSuccessfully added {ordered_food_name} X {order_quantity} to the cart.")
            pause()
            return "break"

    except ValueError:
        print("\n\tQuantity must be in digits.")
        print("\n\tAdditionally, check min|max digits.")
        short_pause()

def order_food():
    while True:
        clear_screen()
        print_header("\tOrder Food.")
        spam.list_food(food_data.search_hits_dict)

        instructions = "\n\tEnter \"0\" to exit."
        instructions += "\n\tOnly digits are accepted."
        instructions += "\n\n\tOption -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option < 1 or option > len(food_data.search_hits_dict):
                print("\n\tInvalid option.")
                short_pause()
            
            else:
                for count, food_name in enumerate(food_data.search_hits_dict, 1):
                    if option == count:
                        ordered_food_name = food_name
                        ordered_food_price = food_data.search_hits_dict.get(food_name)
                        break

                return_code = specify_quantity(ordered_food_name, ordered_food_price)
        
                if return_code == "break":
                    break

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def search_food():
    while True:
        clear_screen()
        print_header(f"\tFood Search Menu.")

        instructions = "\tOnly alphabets and spaces are accepted."
        instructions += "\n\tEnter \"exit\" to go back to the previous menu."
        instructions += "\n\n\tSearch -> "

        food_to_search = input(instructions).lower().strip()

        food_data.search_hits_dict.clear()

        # Regex that only accepts alphabets and spaces.
        regex = r"^[A-Za-z ]*$"
        passed_regex = re.match(regex, food_to_search)

        if passed_regex and food_to_search != "":
            if food_to_search == "exit":
                break

            for food_name in food_data.food_of_the_day_dict:
                if food_name.lower().find(food_to_search) != -1:
                    food_data.search_hits_dict[food_name] = food_data.food_of_the_day_dict.get(food_name)
            
            if len(food_data.search_hits_dict) > 0:
                order_food()

            else:
                print(f"\n\tNo food that is similar to \"{food_to_search}\" found.")
                short_pause()

        else:
            print("\n\tOnly accepts alphabets and spaces.")
            short_pause()

def list_todays_menu():
    clear_screen()
    print_header(f"\t{spam.current_day}'s Menu.")
    spam.list_food(food_data.food_of_the_day_dict)
    pause()

def print_receipt(filename, discount):
    if len(food_data.food_cart_dict) > 0:
        with open(filename, 'w') as f:
            order_number = randint(1, 500)

            data = "Thank you for ordering from SPAM.\n"
            data += f"Order number: #{order_number}\n\n"
            data += "=" * 64
            data += "\nYour order\n"
            data += "=" * 64

            total_price = 0

            for count, food_name in enumerate(food_data.food_cart_dict, 1):
                price_and_quantity_list = food_data.food_cart_dict.get(food_name)

                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity # food_price = food_price * food_quantity
                total_price += food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                data += f"\n{count}. {food_name_and_quantity.ljust(50)} ${food_price:.2f}"

            gross_total_price = f"${total_price:.2f}".rjust(47)
            discounted_price = total_price * (discount / 100.0)
            net_total_price = total_price - discounted_price

            footer = f"\nGross Total: {gross_total_price}"

            discounted_price = str(f"{discounted_price:.2f}")
            discounted_price = f"${discounted_price}".rjust(40)

            footer += f"\nLess {discount}% Discount: {discounted_price}"

            price_to_be_paid = net_total_price

            net_total_price = str(f"{net_total_price:.2f}")
            net_total_price = f"${net_total_price}".rjust(49)

            footer += f"\nNet total: {net_total_price}\n"

            data += "\n"
            data += "=" * 64
            data += f"{footer}"
            data += "=" * 64
            data += "\n\nPlease present this receipt at the counter.\n"
            data += f"Total amount payable -> ${price_to_be_paid:.2f}"

            f.write(data)

            # Opens notepad and the written file.
            Popen(["notepad.exe", filename])

    else:
        print("\n\tCart is empty. There is nothing to be printed.")
        pause()

def modify_quantity(chosen_food):
    clear_screen()
    print_header("\tModify Quantity")

    price_and_quantity_list = food_data.food_cart_dict.get(chosen_food)
    old_quantity = price_and_quantity_list[1]

    print(f"\tOld quantity -> {old_quantity}")

    instructions = "\n\tOnly digits are accepted."
    instructions += "\n\tMin digits - 1, Max digits - 2 ."
    instructions += "\n\n\tQuantity -> "

    try:
        new_quantity = int(input(instructions).strip())

        if new_quantity == 0:
            food_data.food_cart_dict.pop(chosen_food)
            
            print(f"\n\tYou removed {chosen_food} from the cart.")
            pause()

        elif new_quantity < 0:
            print("\n\tNegative values are not accepted.")
            short_pause()

        elif new_quantity > 20:
            print("\n\tExcessive quantity are not accepted.")
            short_pause()

        else:
            price_and_quantity_list[1] = new_quantity
            food_data.food_cart_dict[chosen_food] = price_and_quantity_list

            print(f"\n\tUpdated quantity to X {new_quantity}.")
            pause()
    
    except ValueError:
        print("\n\tOnly digits are accepted.")
        short_pause()  

def modify_cart():
    while True:
        upper_bound = len(food_data.food_cart_dict)

        if upper_bound > 0:
            clear_screen()
            print_header("\tModify Cart")

            for count, food_name in enumerate(food_data.food_cart_dict, 1):
                price_and_quantity_list = food_data.food_cart_dict.get(food_name)

                # Format of food_cart -> Chicken Rice : [2.50(price), 5(quantity)]
                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                food_price = f"${food_price:.2f}"

                print(f"\t{count}. {food_name_and_quantity.ljust(50)} {food_price}")

            instructions = "\n\tEnter \"0\" to exit."
            instructions += "\n\tOnly digits are accepted."
            instructions += "\n\n\tOption -> "

            try:
                option = int(input(instructions).strip())

                if option == 0:
                    break

                elif option < 1 or option > upper_bound:
                    print(f"\n\tFood chosen must be between 1 to {upper_bound}.")
                    short_pause()

                else:
                    for count, food_name in enumerate(food_data.food_cart_dict, 1):
                        if option == 1:
                            chosen_food = food_name
                            break

                    modify_quantity(chosen_food)

            except ValueError:
                print("\n\tOnly digits are accepted.")
                short_pause()

        else:
            return "empty"

def make_payment(amount_to_pay):
    while True:
        clear_screen()
        print_header("\tPayment")

        print(f"\tAmount to pay -> ${amount_to_pay:.2f}")

        instructions = "\n\tOnly digits(floating points) are accepted."
        instructions += "\n\tEnter \"0\" to cancel payment."
        instructions += "\n\tPlease enter amount to pay -> $"

        try:
            amount_from_customer = float(input(instructions).strip())

            if amount_from_customer == 0:
                print("\n\tYou have chosen to cancel payment.")
                short_pause()
                break

            elif amount_from_customer < amount_to_pay:
                print("\n\tPlease provide exact amount or more.")
                short_pause()

            else:
                customers_change = amount_from_customer - amount_to_pay
                print(f"\n\tChange -> ${customers_change:.2f}")
                print("\n\tThank you for supporting SPAM!")
                pause()

                return "payment made"

        except ValueError:
            print("\n\tOnly digits(floating points) are accepted.")
            short_pause()

def list_order(discount):
    while True:
        clear_screen()

        if len(food_data.food_cart_dict) > 0:
            print_header("\tYour order.")

            total_price = 0

            for count, food_name in enumerate(food_data.food_cart_dict, 1):
                price_and_quantity_list = food_data.food_cart_dict.get(food_name)

                # Format of food_cart -> Chicken Rice : [2.50(price), 5(quantity)]
                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity
                total_price += food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                food_price = f"${food_price:.2f}"

                print(f"\t{count}. {food_name_and_quantity.ljust(50)} {food_price}")

            gross_total_price = f"${total_price:.2f}".rjust(47)
            discounted_price = total_price * (discount / 100.0)
            net_total_price = total_price - discounted_price

            amount_to_pay = net_total_price

            footer = f"\tGross Total: {gross_total_price}"

            discounted_price = str(f"{discounted_price:.2f}")
            discounted_price = f"${discounted_price}".rjust(40)

            footer += f"\n\tLess {discount}% Discount: {discounted_price}"

            net_total_price = str(f"{net_total_price:.2f}")
            net_total_price = f"${net_total_price}".rjust(49)

            footer += f"\n\tNet total: {net_total_price}"

            print_header(f"{footer}")

            instructions = "\n\tOnly 'q', 'm', 's', 'e', 'p' are accepted."
            instructions += "\n\n\tEnter \"q\" to go back to the main menu."
            instructions += "\n\tEnter \"m\" to modify cart."
            instructions += "\n\tEnter \"s\" to print out receipt."
            instructions += "\n\tEnter \"e\" to empty cart."
            instructions += "\n\tEnter \"p\" to make payment."
            instructions += "\n\n\tOption -> "

            option = input(instructions).lower().strip()
           
            if option == 'q':
                break

            elif option == 's':
                print_receipt(receipt_file_path, discount)

                print("\n\tSave successful.")
                print("\n\tPlease proceed to the counter with the receipt in hand.")
                food_data.food_cart_dict.clear()

                pause()
                break

            elif option == 'm':
                if modify_cart() == "empty":
                    break

            elif option == 'e':
                food_data.food_cart_dict.clear()
                clear_screen()
                print("\tEmptied food cart.")
                pause()
                break

            elif option == 'p':
                if make_payment(amount_to_pay) == "payment made":
                    food_data.food_cart_dict.clear()
                    break
            
            else:
                print("\n\tOnly 'q', 'm', 's', 'e', 'p' are accepted.")
                short_pause()
            
        else:
            print("\n\tFood cart is empty.")
            pause()
            break

def user_menu(username, discount):
    while True:
        clear_screen()
        print_header("\tAutomated Food Menu.")
        print(f"\tWelcome {username}")

        print("\n\t1. Display today's menu.")
        print("\t2. Search and order food.")
        print("\t3. Display cart.")

        instructions = "\n\tOnly digits are accepted."
        instructions += "\n\tEnter \"0\" to exit."
        instructions += "\n\n\tChoice -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                print("\n\tGoodbye.")
                break

            elif option == 1:
                list_todays_menu()

            elif option == 2:
                search_food()

            elif option == 3:
                list_order(discount)

        except KeyboardInterrupt:
            print("\n\n\tDetected CTRL+C, logging out.")
            print("\tGoodbye.")
            short_pause()
            break

        except ValueError:
            print("\n\tOnly accepts digits.")
            short_pause()

        except Exception as error:
            print(f"\n\t Error -> {error}")
            pause()

def change_food_name(selected_day, selected_day_food_dict, selected_food_name):
    clear_screen()
    print(f"\tChange Food Name for -> {selected_food_name}")

    instructions = "\n\tOnly alphabets and spaces are accepted."
    instructions += "\n\tEnter New Food Name -> "

    new_food_name = input(instructions).strip()

    # ^ - Match beginning of string , $ - Match end of string
    # [A-Za-z ] - accepts only alphabets and spaces
    regex = r"^[A-Za-z ]*$"
    regex_passed = re.match(regex, new_food_name)

    if regex_passed:
        duplicate_food_name_found = False

        for food_name in selected_day_food_dict:
            if new_food_name.lower() == food_name.lower():
                duplicate_food_name_found = True

                print(f"\n\tThere is already an existing \"{new_food_name}\" in the menu.")
                pause()
                break

        if duplicate_food_name_found == False:
            selected_day_food_dict[new_food_name] = selected_day_food_dict.pop(selected_food_name)
            food_data.food_dict[selected_day] = selected_day_food_dict

            food_data.food_cart_dict.clear()
            spam.convert_nested_dict_into_data_and_store_it_in_file(food_file, food_data.food_dict)

            print(f"\n\tChanged {selected_food_name} to {new_food_name}.")
            short_pause()

            return "updated"

    else:
        print("\n\tOnly alphabets and spaces are accepted.")
        short_pause()

def update_food_price(selected_day, selected_day_food_dict, selected_food_name):
    old_price = selected_day_food_dict.get(selected_food_name)

    clear_screen()
    print_header("\tUpdate Food Price.")
    print(f"\tOld Price -> ${old_price:.2f}")

    # try-except because regex is not the right tool for confirming if input is indeed a float.
    try:
        instructions = "\n\tOnly accepts floating point numbers."
        instructions += "\n\tFormat -> xx.yy or x.y"
        instructions += "\n\n\tNew price -> "

        new_price = float(input(instructions).strip())

        if new_price > 0:
            selected_day_food_dict[selected_food_name] = new_price
            food_data.food_dict[selected_day] = selected_day_food_dict
            food_data.food_cart_dict.clear()

            spam.convert_nested_dict_into_data_and_store_it_in_file(food_file, food_data.food_dict)

            print(f"\n\tUpdated price from ${old_price:.2f} to ${new_price:.2f} .")
            pause()

            return "updated"
        
        else:
            print("\n\tNew price must not be zero or negative.")
            short_pause()

    except ValueError:
        print("\n\tOnly accepts floating point numbers.")
        short_pause()

def delete_food(selected_day, selected_day_food_dict, selected_food_name):
    if len(selected_day_food_dict) > 1:
        food_data.food_cart_dict.clear()

        # 1. Delete 2. Update nested dictionary. 3. Save updated nested dictionary to file.
        selected_day_food_dict.pop(selected_food_name)
        food_data.food_dict[selected_day] = selected_day_food_dict
        spam.convert_nested_dict_into_data_and_store_it_in_file(food_file, food_data.food_dict)

        print(f"\n\tDeleted {selected_food_name} from {selected_day}'s menu.")

        pause()
        return "deleted"

    else:
        print("\n\tThe last remaining food must not be deleted.")
        pause()

def edit_food_name_or_food_price_or_deleted_food(selected_day, selected_day_food_dict, selected_food_name):
    while True:
        clear_screen()
        print_header(f"\t{selected_food_name}.")

        print("\t1. Change food name to something else.")
        print("\t2. Change food price to something else.")
        print("\t3. Delete food.")

        try:
            instructions = "\n\tOnly digits are accepted."
            instructions += "\n\tEnter \"0\" to exit."
            instructions += "\n\n\tSelect Food -> "

            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option < 0 or option > 3:
                print("\n\tOption chosen must be in the range of 1 -> 3.")
                short_pause()

            elif option == 1:
                return_code = change_food_name(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "updated":
                    return "updated"

            elif option == 2:
                return_code = update_food_price(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "updated":
                    return "updated"

            elif option == 3:
                return_code = delete_food(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "deleted":
                    return "deleted"

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def choose_food(selected_day_food_dict, selected_day):
    while True:
        clear_screen()
        print_header(f"\t{selected_day}'s Food Menu.")

        spam.list_food(selected_day_food_dict)

        instructions = "\n\tOnly digits are accepted."
        instructions += "\n\tEnter \"0\" to exit."
        instructions += "\n\n\tSelect Food -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option < 0 or option > len(selected_day_food_dict):
                print(f"\n\tFood chosen must be in the range of 1 to {len(selected_day_food_dict)}.")
                short_pause()

            else:
                for count, food_name in enumerate(selected_day_food_dict, 1):
                    if option == count:
                        selected_food_name = food_name
                        break

                return_code = edit_food_name_or_food_price_or_deleted_food(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "updated" or return_code == "deleted":
                    return "break"

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def add_food(selected_day):
    selected_day_food_dict = food_data.food_dict.get(selected_day)

    while True:
        clear_screen()
        print_header(f"\tAdd food for {selected_day}")
        spam.list_food(selected_day_food_dict)

        instructions = "\n\tOnly accepts alphabets and spaces."
        instructions += "\n\tEnter \"exit\" to exit."
        instructions += "\n\n\tEnter new food name -> "

        new_food_name = input(instructions).strip()

        if new_food_name == "exit":
            break

        duplicate = False
        
        # Check for the presence of the same key in the dictionary.
        for food_name in selected_day_food_dict:
            if new_food_name.lower() == food_name.lower():
                duplicate = True
                break

        regex = r"^[A-Za-z ]*$"
        passed_regex = re.match(regex, new_food_name)

        # Passed regex, not empty, not duplicate.
        if passed_regex and new_food_name != "" and duplicate == False:
            try:
                new_food_price = float(input("\tEnter new food price -> ").strip())

                # Clear food cart because we do not want food cart to contain stale data.
                food_data.food_cart_dict.clear()

                selected_day_food_dict[new_food_name] = new_food_price
                food_data.food_dict[selected_day] = selected_day_food_dict
                spam.convert_nested_dict_into_data_and_store_it_in_file(food_file, food_data.food_dict)

                print(f"\n\tSuccessfully added {new_food_name} -> ${new_food_price:.2f} .")
                short_pause()

                return "added"

            except ValueError:
                print("\n\tOnly accepts floating point numbers")
                short_pause()
        
        else:
            print("\n\tPlease recheck input.")
            print("\tIt may be a duplicate OR")
            print("\tFood name doesn't contain alphabets.")
            short_pause()

def add_delete_edit_menu(selected_day, selected_day_food_dict):
    while True:
        clear_screen()
        print_header("\tAdd, Delete, Edit food.")

        print("\t1. Add Food.")
        print("\t2. Delete/Edit Food.")
        
        try:
            instructions = "\n\tOnly accepts digits."
            instructions += "\n\tEnter \"0\" to exit."
            instructions += "\n\n\tOption -> "          

            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option == 1:
                return_code = add_food(selected_day)

                if return_code == "added":
                    break

            elif option == 2:
                return_code = choose_food(selected_day_food_dict, selected_day)

                if return_code == "break":
                    break

            else:
                print("\n\tInvalid option.")
                short_pause()

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def edit_food():
    while True:
        clear_screen()
        print_header("\tEdit Food.")

        for count, day_of_the_week in enumerate(spam.weekdays, 1):
            print(f"\t{count}. {day_of_the_week}")

        try:
            instructions = "\n\tOnly digits are accepted."
            instructions += "\n\tEnter \"0\" to exit."
            instructions += "\n\n\tSelect Day -> "

            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option < 0 or option > len(spam.weekdays):
                print("\n\tOnly option 1-7 are accepted.")
                short_pause()

            else:
                selected_day = spam.weekdays[option - 1]
                selected_day_food_dict = food_data.food_dict.get(selected_day)

                add_delete_edit_menu(selected_day, selected_day_food_dict)

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def admin_menu(username):
    while True:
        clear_screen()
        print_header(f"\tAdmin console.\n\tProceed with caution.")
        
        print(f"\tWelcome {username}")
        print("\n\t1. Edit food.")

        instructions = "\n\tEnter \"0\" to exit."
        instructions += "\n\tOnly accepts digits."
        instructions += "\n\n\tOption -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option == 1:
                edit_food()
            
            else:
                print("\n\tOption invalid.")
                short_pause()

        except KeyboardInterrupt:
            print("\n\n\tDetected CTRL+C, logging out.")
            print("\tGoodbye.")
            short_pause()
            break

        except ValueError:
            print("\n\tOnly accepts digits.")
            short_pause()

def authenticate_user(username, password):
    db_file_exist = path.exists(db_file)

    if db_file_exist:
        try:
            sqlite_connection = sqlite3.connect(db_file)
            cursor = sqlite_connection.cursor()

            query = f"SELECT username, password, is_admin, discount FROM credentials WHERE "
            query += f"username = \"{username}\" and password = \"{password}\" LIMIT 1"

            cursor.execute(query)
            result = cursor.fetchall()

            return result

        except sqlite3.Error as error:
            print(f"\n\tError -> {error}")
            sys.exit(1)
        
        finally:
            # If sqlite connection is active, close it.
            if sqlite_connection:
                sqlite_connection.close()

    else:
        print("\n\tUnable to find DB file.")
        sys.exit(1)

def create_user(username, password, is_admin, discount):
    db_file_exist = path.exists(db_file)

    if db_file_exist:
        '''
        CREATE TABLE [credentials] (
                [user_id] integer primary key,
                [username] text not null unique,
                [password] text not null,
                [is_admin] text not null,
                [discount] text not null
        );
        '''
        sqlite_connection = sqlite3.connect(db_file)
        cursor = sqlite_connection.cursor()

        query = f"INSERT INTO credentials (username, password, is_admin, discount) VALUES (\"{username}\", \"{password}\", \"{is_admin}\", \"{discount}\")"

        try: 
            cursor.execute(query)
            sqlite_connection.commit()
            return "ok"
        
        except sqlite3.Error:
            return "not ok"

        finally:
            if sqlite_connection:
                sqlite_connection.close()
           
def register():
    while True:
        clear_screen()
        print_header("\tRegister new user.")

        instructions = "\tFor username, only alphabets are accepted."
        instructions += "\n\n\tFor passwords:"
        instructions += "\n\tAt least 1 uppercase, 1 lowercase, 1 number and 1 special character."
        instructions += "\n\tLeading and Trailing whitespaces for passwords will be removed."

        print(instructions)

        new_username = input("\n\tEnter new username -> ").lower().strip()

        regex = r"^[A-Za-z]+$"
        username_regex_passed = re.match(regex, new_username)

        if username_regex_passed:
            new_password = input("\tEnter new password -> ").strip()

            lower_regex = re.compile(r'[a-z]+')
            upper_regex = re.compile(r'[A-Z]+')
            digit_regex = re.compile(r'[0-9]+')
            special_char_regex = re.compile(r'\W+')

            if len(new_password) < 8:
                print("\n\tPassword must contain at least 8 characters.")
                short_pause()

            elif lower_regex.findall(new_password) == []:
                print("\n\tPassword must contain at least one lowercase character.")
                short_pause()

            elif upper_regex.findall(new_password) == []:
                print("\n\tPassword must contain at least one upper.")
                short_pause()

            elif digit_regex.findall(new_password) == []:
                print("\n\tPassword must contain at least one digit.")
                short_pause()

            elif special_char_regex.findall(new_password) == []:
                print("\n\tPassword must contain at least one special char.")
                short_pause()

            else:
                hashed_password = md5(new_password.encode()).hexdigest()
                return_code = create_user(new_username, hashed_password, "no", "5")

                if return_code == "ok":
                    print(f"\n\tUser {new_username} created!")
                    pause()
                    break

                else:
                    print(f"\n\tThere is an existing user. Unable to create account.")
                    print("\tPlease choose a unique username.")
                    pause()

        else:
            print("\n\tPlease check your input for username again.")
            short_pause()

def login_menu():
    while True:
        clear_screen()
        print_header("\tLogin Menu.")

        instructions = "\tFor username, only alphabets are accepted."
        instructions += "\n\tAbove rule does not apply for password."
        instructions += "\n\n\tEnter \"register\" to register new user."
        instructions += "\n\tPress \"CTRL+C\" to exit."

        print(instructions)

        try:
            username = input("\n\tUsername -> ").lower().strip()
            
            if username == "register":
                register()
            
            else:
                regex = r"^[A-Za-z]*$"
                passed_regex = re.match(regex, username)

                if passed_regex and username != "":                
                    password = input("\tPassword -> ")

                    if password != "":
                        hashed_password = md5(password.encode()).hexdigest()

                        authentication_results = authenticate_user(username, hashed_password)

                        if len(authentication_results) > 0:
                            # [('admin', '21232f297a57a5a743894a0e4a801fc3', 'yes', '15')]
                            # Is a tuple contained in a list.
                            # list[0] -> authentication data
                            authentication_results = authentication_results[0]

                            # Instance is only created once we have results from authentication.
                            login_data = Login(authentication_results[0], authentication_results[1], authentication_results[2], int(authentication_results[3]))
                            
                            if login_data.is_admin == "yes":
                                admin_menu(login_data.username)

                                # Destroy instance.
                                del login_data

                            else:
                                user_menu(login_data.username, login_data.discount)
                                del login_data

                        else:
                            print("\n\tEither username or password is wrong.")
                            short_pause()

                    else:
                        print("\n\tPassword must not be empty.")
                        short_pause()
                        
                else:
                    print("\n\tOnly accepts alphabets and no spaces for username.")
                    print("\tCheck your input again.")
                    short_pause()

        except KeyboardInterrupt:
            print("\n\n\tDetected CTRL+C, terminating program.")
            print("\tGoodbye.")
            break
        
        except Exception as error:
            print(f"Error -> {error}")
            short_pause()

def cover():
    message = "        I am a hacker, enter my world...\n"
    message += "    Mine is a world that begins with school...\n"
    
    for index in range(len(message)):
        clear_screen()
        print(message[0:index])
        sleep(0.05)

    short_pause()
    
# For Data() Class
food_dict = dict()
food_cart_dict = dict()
food_of_the_day_dict = dict()
search_hits_dict = dict()

# For loading of food, creds and saving of orders.
db_file = getcwd() + "\\creds.db"
food_file = getcwd() + "\\food.txt"
receipt_file_path = getcwd() + "\\order.txt"

# Instance of Data() class.
spam = Data(food_file, db_file)

# Instance of Food() class.
food_data = Food(food_dict, food_cart_dict, food_of_the_day_dict, search_hits_dict)

# 2 important components:
# food_dict and food_of_the_day_dict which is crucial for the running of the program. 
food_data.food_dict = spam.load_data_to_nested_dict(spam.load_data_from_file())
food_data.food_of_the_day_dict = spam.get_todays_menu(food_data.food_dict)

#cover()
login_menu()