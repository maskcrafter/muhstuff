import socket
import re
import sys

from time import sleep
from os import system, getcwd, path
from calendar import day_name
from datetime import date
from random import randint
from hashlib import md5
from subprocess import Popen

def pause():
    print()
    system("pause")

def short_pause():
    sleep(1.2)

def clear_screen():
    system("cls")

def connect_to_server():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
     
def download_data():
    try:
        client_socket = connect_to_server()
        client_socket.connect((HOST, PORT))
        client_socket.send(b'download')

        data = client_socket.recv(2048)
        
        return eval(data)
    
    except Exception as error:
        print(error)
        sys.exit(1)

    finally:
        client_socket.close()

def upload_data():
    try:
        data = str(food_dict).encode()

        client_socket = connect_to_server()
        client_socket.connect((HOST, PORT))

        client_socket.send(b'upload')

        if client_socket.recv(255).decode() == "ok":
            client_socket.send(data)
    
    except Exception as error:
        print(error)
        sys.exit(1)

    finally:
        client_socket.close()

def convert_data_to_nested_dict(food_list):
    temp_food_dict = dict()

    for day_of_the_week in WEEKDAYS:
        food_name_and_price_dict = dict()

        for food in food_list:
            food_day, food_name, food_price = food.split(',')

            if food_day == day_of_the_week:
                food_name_and_price_dict[food_name] = float(food_price)
        
        temp_food_dict[day_of_the_week] = food_name_and_price_dict

    return temp_food_dict

def print_header(header_message):
    print('\t' + '=' * 64)
    print(f"{header_message}")
    print('\t' + '=' * 64)

def list_food(local_food_dict):
    for count, food_name in enumerate(local_food_dict, 1):
        food_price = local_food_dict[food_name]
        print(f"\t{count}. {food_name.ljust(35)} ${food_price:.2f}")

def list_todays_food_menu():
    clear_screen()

    if len(todays_food_dict) > 0:
        print_header(f"\t{DAY_OF_THE_WEEK}'s Menu.")
        list_food(todays_food_dict)
        
    else:
        print(f"\t{DAY_OF_THE_WEEK}'s food menu is empty.")
    
    pause()

def order_food(local_food_dict):
    global food_cart_dict

    while True:
        clear_screen()
        print_header(f"\tOrder food")
        list_food(local_food_dict)

        try:
            instructions = "\n\tEnter '0' to exit."
            instructions += "\n\tOnly digits are accepted."
            instructions += "\n\n\tOption -> "

            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option < 1 or option > len(local_food_dict):
                print("\n\tInvalid option.")
                short_pause()
            
            else:
                for count, food_name in enumerate(local_food_dict, 1):
                    if option == count:
                        ordered_food_name = food_name
                        ordered_food_price = local_food_dict.get(food_name)
                        break

                clear_screen()
                print_header(f"\t{ordered_food_name}'s page.")

                instructions = "\tOnly digits are accepted."
                instructions += "\n\tQuantity must not be greater than 20."
                instructions += "\n\n\tQuantity -> "
                
                try:
                    order_quantity = int(input(instructions).strip())

                    if order_quantity == 0:
                        print(f"\n\tYou have cancelled ordering {ordered_food_name}.")
                        short_pause()
                        break
                    
                    elif order_quantity < 0:
                        print("\n\tNegative values are not accepted.")
                        short_pause()

                    elif order_quantity > 20:
                        print("\n\tExcessive quantities are not accepted.")
                        short_pause()
                    
                    else:
                        price_and_quantity_list = [ordered_food_price, order_quantity]
                        food_cart_dict[ordered_food_name] = price_and_quantity_list

                        print(f"\n\tSuccessfully added {ordered_food_name} X {order_quantity} to the cart.")
                        pause()
                        break
                
                except ValueError:
                    print(f"\n\tOnly accepts digits.")
                    short_pause()

        except ValueError:
            print(f"\n\tOnly accepts digits.")
            short_pause()

def search_food():
    while True:
        clear_screen()
        print_header(f"\tFood-Search Menu")

        instructions = "\tOnly alphabets and spaces are accepted."
        instructions += "\n\tEnter 'exit' to go back to the previous menu."
        instructions += "\n\n\tSearch -> "
        
        food_to_search = input(instructions).lower().strip()

        # https://stackoverflow.com/questions/30994738/how-to-make-input-only-accept-a-z-etc
        # https://pythex.org/
        regex = r"^[A-Za-z ]*$"
        passed_regex = re.match(regex, food_to_search)

        search_hits_dict = dict()

        if passed_regex and food_to_search != "":
            if food_to_search == "exit":
                break
      
            for food_name in todays_food_dict:
                if food_name.lower().find(food_to_search) != -1:
                    search_hits_dict[food_name] = todays_food_dict.get(food_name)

            if len(search_hits_dict) > 0:
                order_food(search_hits_dict)

            else:
                print(f"\n\tSearch founds no food similar to \"{food_to_search}\".")
                short_pause()
 
        else:
            print("\n\tPlease check your input again.")
            short_pause()

def make_payment(amount_to_pay, discount_rate):
    while True:
        clear_screen()
        print_header("\tPayment")

        print(f"\tAmount to pay -> ${amount_to_pay:.2f}")

        instructions = "\n\tOnly digits are accepted."
        instructions += "\n\tEnter '0' to cancel payment."
        instructions += "\n\n\tPlease enter amount to pay -> $"

        try:
            amount_from_customer = float(input(instructions).strip())

            if amount_from_customer == 0:
                print("\n\tYou have cancelled payment.")
                short_pause()
                break

            elif amount_from_customer < amount_to_pay:
                print("\n\tPlease provide exact amount or more.")
                short_pause()

            else:
                customers_change = amount_from_customer - amount_to_pay
                print(f"\n\tChange -> ${customers_change:.2f}")

                order_number = randint(1, 500)
                RECEIPT_FILE_PATH = getcwd() + f"\\order-{order_number}.txt"

                # print_receipt(filename, discount_rate, order_number, amount_from_customer, customers_change)
                print_receipt(RECEIPT_FILE_PATH, discount_rate, order_number, amount_from_customer, customers_change)
                Popen(["notepad.exe", RECEIPT_FILE_PATH])

                print("\n\tThank you for supporting SPAM!")
                pause()

                return "payment made"

        except ValueError:
            print("\n\tOnly digits are accepted.")
            short_pause()

def modify_quantity(chosen_food):
    clear_screen()
    print_header(f"\t{chosen_food}.")

    price_and_quantity_list = food_cart_dict.get(chosen_food)
    old_quantity = price_and_quantity_list[1]

    print(f"\tOld quantity -> {old_quantity}")

    instructions = "\n\tOnly digits are accepted."
    instructions += "\n\tQuantity must not be greater than 20."
    instructions += "\n\n\tQuantity -> "

    try:
        new_quantity = int(input(instructions).strip())

        if new_quantity == 0:
            food_cart_dict.pop(chosen_food)

            print(f"\n\tYou removed {chosen_food} from the cart.")
            pause()

        elif new_quantity < 0:
            print("\n\tNegative values are not accepted.")
            short_pause()

        elif new_quantity > 20:
            print("\n\tExcessive quantities are not accepted.")
            short_pause()

        else:
            price_and_quantity_list[1] = new_quantity
            food_cart_dict[chosen_food] = price_and_quantity_list

            print(f"\n\tUpdated {chosen_food} to X {new_quantity}.")
            pause()

    except ValueError:
        print(f"\n\tOnly digits are accepted.")
        short_pause()

def modify_cart():
    while True:
        upper_bound = len(food_cart_dict)

        if upper_bound > 0:
            clear_screen()
            print_header("\tModify Cart.")

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict.get(food_name)

                food_quantity = price_and_quantity_list[1]
                food_name_and_quantity = f"{food_name} X {food_quantity}"

                print(f"\t{count}. {food_name_and_quantity.ljust(50)}")

            instructions = "\n\tEnter '0' to exit."
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
                    for count, food_name in enumerate(food_cart_dict, 1):
                        if option == count:
                            chosen_food = food_name
                            break

                    modify_quantity(chosen_food)

            except ValueError:
                print("\n\tOnly digits are accepted.")
                short_pause()
            
        else:
            return "empty cart"

def list_order(discount_rate):    
    global food_cart_dict

    while True:
        clear_screen()

        if len(food_cart_dict) > 0:
            print_header("\tYour order.")

            total_price = 0

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict.get(food_name)
                
                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity
                total_price += food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                food_price = f"${food_price:.2f}"

                print(f"\t{count}. {food_name_and_quantity.ljust(50)} {food_price}")
            
            gross_total_price = f"${total_price:.2f}".rjust(47)
            discounted_price = total_price * (discount_rate / 100.0)
            net_total_price = total_price - discounted_price

            amount_to_pay = net_total_price

            footer = f"\tGross Total: {gross_total_price}"

            discounted_price = str(f"{discounted_price:.2f}")
            discounted_price = f"${discounted_price}".rjust(38)
            
            footer += f"\n\tLess {discount_rate}% Discount: {discounted_price}"
        
            net_total_price = str(f"{net_total_price:.2f}")
            net_total_price = f"${net_total_price}".rjust(45)

            print("\t" + "-" * 64)
            print(footer)
            print("\t" + "-" * 64)
            print(f"\tTotal payable: {net_total_price}")
            print("\t" + "-" * 64)

            instructions = "\n\tEnter 'q' to go back to the main menu."
            instructions += "\n\tEnter 'm' to modify cart."
            instructions += "\n\tEnter 'p' to make payment."
            instructions += "\n\tEmpty 'e' to empty cart."
            instructions += "\n\n\tOption -> "
            
            option = input(instructions).lower().strip()
            
            if option == 'q':
                break

            elif option == 'm':
                if modify_cart() == "empty cart":
                    break

            elif option == 'p':
                if make_payment(amount_to_pay, discount_rate) == "payment made":
                    food_cart_dict.clear()
                    break

            elif option == 'e':
                food_cart_dict.clear()
                clear_screen()

                print("\tEmptied food cart.")
                pause()
                break

            else:
                print("\n\tOnly 'q', 'm', 'p', 'e' are accepted.")
                short_pause()              
        
        else:
            print("\tFood cart is empty.")
            pause() 
            break

def print_receipt(filename, discount_rate, order_number, amount_from_customer, customers_change):
    if len(food_cart_dict) > 0:
        with open(filename, 'w') as f:

            data = "=" * 64
            data += f"\nOrder #{order_number}\n"
            data += "=" * 64

            total_price = 0

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict.get(food_name)

                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity # food_price = food_price * food_quantity
                total_price += food_price   # total_price = total_price + food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                data += f"\n{count}. {food_name_and_quantity.ljust(50)} ${food_price:.2f}"

            gross_total_price = f"${total_price:.2f}".rjust(47)
            discounted_price = total_price * (discount_rate / 100.0)
            net_total_price = total_price - discounted_price

            footer = f"\nGross Total: {gross_total_price}"

            discounted_price = str(f"{discounted_price:.2f}")
            discounted_price = f"${discounted_price}".rjust(38)

            footer += f"\nLess {discount_rate}% Discount: {discounted_price}"

            net_total_price = str(f"{net_total_price:.2f}")
            net_total_price = f"${net_total_price}".rjust(45)

            data += "\n"
            data += "-" * 64
            data += f"{footer}\n"
            data += "-" * 64
            data += f"\nTotal payable: {net_total_price}\n"
            data += "-" * 64
            data += f"\n\nYou paid -> ${amount_from_customer:.2f}\n"
            data += f"Your change -> ${customers_change:.2f}\n"
            data += "\nThank you for supporting SPAM."

            f.write(data)
        
    else: 
        print(f"\n\tCart is empty. There is nothing to be printed.")
        pause()

def user_menu(username, discount_rate):
    while True:
        clear_screen()
        print_header("\tAutomated Food Menu.")

        print(f"\tWelcome {username}.\n")
        print("\t1. Display today's menu.")
        print("\t2. Search food.")
        print("\t3. Display cart.")
        
        instructions = "\n\tOnly digits are accepted."
        instructions += "\n\tEnter '0' to exit."
        instructions += "\n\n\tChoice -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                print("\n\tGoodbye.")
                break

            elif option == 1:
                list_todays_food_menu()
            
            elif option == 2:
                search_food()
           
            elif option == 3:
                list_order(discount_rate)
        
        except KeyboardInterrupt:
            print("\n\n\tInterrupted by \"CTRL + C\"")
            print("\tLogging out.")
            short_pause()
            break

        except ValueError:
            print(f"\n\tOnly accepts digits.")
            short_pause()

def shutdown_server():
    try:
        client_socket = connect_to_server()
        client_socket.connect((HOST, PORT))
        
        client_socket.send(b'shutdown')

        print("\n\tShutdown completed.")

    except Exception as error:
        print(f"\n\t{error}")
        pause()

    finally:
        client_socket.close()
        sys.exit(0)

def add_food(selected_day):
    global food_dict
    global food_cart_dict

    selected_day_food_dict = food_dict[selected_day]

    while True:
        clear_screen()
        print_header(f"\tAdd food for {selected_day}.")
        list_food(selected_day_food_dict)

        instructions = "\n\tOnly accepts alphabets and spaces."
        instructions += "\n\tEnter 'exit' to exit."
        instructions += "\n\n\tEnter new food name -> "

        new_food_name = input(instructions).strip()

        if new_food_name == "exit":
            break

        duplicate = False

        # Check for the presence of same key in the dictionary.
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

                selected_day_food_dict[new_food_name] = new_food_price 
                food_dict[selected_day] = selected_day_food_dict
                food_cart_dict.clear()

                update_data()

                print(f"\n\tSuccessfully added {new_food_name} -> ${new_food_price:.2f} .")
                short_pause()

                return "added"

            except ValueError:
                print(f"\n\tPrice must be in floating point format.")
                short_pause()

        else:
            print("\n\tOnly accepts alphabets and spaces.")
            print("\n\tFood name must not be empty and duplicates of existing food.")
            short_pause()

def delete_food(selected_day, selected_day_food_dict, selected_food_name):
    global food_dict
    global food_cart_dict
    
    if len(selected_day_food_dict) > 1:
        food_cart_dict.clear()

        selected_day_food_dict.pop(selected_food_name)
        food_dict[selected_day] = selected_day_food_dict
       
        print(f"\n\tDeleted {selected_food_name} from {selected_day}'s menu.")
        update_data()
        pause()

        return "deleted"
    
    else:
        print("\n\tThe last remaining food must not be deleted.")
        pause()
        
def update_data():
    global food_dict

    upload_data()
    food_dict = convert_data_to_nested_dict(download_data())

def change_food_name(selected_day, selected_day_food_dict, selected_food_name):
    global food_dict
    global food_cart_dict

    clear_screen()
    print(f"\tChange Food Name for -> {selected_food_name}")

    instructions = "\n\tOnly alphabets and spaces are accepted."
    instructions += "\n\tEnter New Food Name -> "
    
    new_food_name = input(instructions).strip()

    # ^ - Match beginning of string , $ - Match end of string
    # [A-Za-z ] - accepts only alphabets and spaces
    regex = r"^[A-Za-z ]*$"

    if re.match(regex, new_food_name):
        duplicate_food_name_found = False

        for food_name in selected_day_food_dict:
            if new_food_name.lower() == food_name.lower():
                duplicate_food_name_found = True

                print(f"\n\tThere is already an existing \"{new_food_name}\" in the menu.")
                pause()
                break

        if duplicate_food_name_found == False:
            selected_day_food_dict[new_food_name] = selected_day_food_dict.pop(selected_food_name)
            food_dict[selected_day] = selected_day_food_dict

            food_cart_dict.clear()
            update_data()

            print(f"\n\tChanged {selected_food_name} to {new_food_name}.")
            short_pause()

            return "updated"

    else:
        print("\n\tOnly alphabets and spaces are accepted.")
        short_pause()

def update_food_price(selected_day, selected_day_food_dict, selected_food_name):
    global food_dict
    global food_cart_dict

    old_price = selected_day_food_dict.get(selected_food_name)

    clear_screen()
    print_header("\tUpdate food price.")
    print(f"\tOld price -> ${old_price:.2f}")
    
    try: 
        instructions = "\n\tOnly accepts floating point numbers."
        instructions += "\n\tFormat -> xx.yy or x.y"
        instructions += "\n\n\tNew price -> "

        new_price = float(input(instructions).strip())

        selected_day_food_dict[selected_food_name] = new_price
        food_dict[selected_day] = selected_day_food_dict
        food_cart_dict.clear()

        update_data()

        print(f"\n\tUpdated price from ${old_price:.2f} to ${new_price:.2f} .")
        pause()

        return "updated"
    
    except ValueError:
        print(f"\n\tPrice must be in floating point format.")
        short_pause()

def edit_food_name_or_food_price_or_delete_food(selected_day, selected_day_food_dict, selected_food_name):
    while True:
        clear_screen()
        print_header(f"\t{selected_food_name}")

        print("\t1. Change food name to something else.")
        print("\t2. Change food price to something else.")
        print("\t3. Delete food.")

        try:
            instructions = "\n\tOnly digits are accepted."
            instructions += "\n\tEnter '0' to exit."
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
            print(f"\n\tOnly digits are accepted.")
            short_pause()

def choose_food(selected_day_food_dict, selected_day):
    while True:
        clear_screen()
        print_header(f"\t{selected_day}'s Food Menu.")

        list_food(selected_day_food_dict)
        
        instructions = "\n\tOnly digits are accepted."
        instructions += "\n\tEnter '0' to exit."
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
                
                # When food name, food price have been updated, breaks loop and return to day selection to prevent stale data.
                return_code = edit_food_name_or_food_price_or_delete_food(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "updated" or return_code == "deleted":
                    return "break"

        except ValueError:
            print(f"\n\tOnly digits are accepted.")
            short_pause()

def add_delete_edit_menu(selected_day, selected_day_food_dict):
    while True:
        clear_screen()
        print_header(f"\t{selected_day}.")

        print("\t1. Add Food.")
        print("\t2. Delete/Edit Food.")

        try:
            instructions = "\n\tOnly accepts digits."
            instructions += "\n\tEnter '0' to exit."
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
                print("\n\tInvalid input.")
                short_pause()

        except ValueError:
            print(f"\n\tOnly digits are accepted.")
            short_pause()

def edit_food():
    while True:
        clear_screen()
        print_header("\tEdit Food.")

        for count, day_of_the_week in enumerate(WEEKDAYS, 1):
            print(f"\t{count}. {day_of_the_week}")
        
        try:
            instructions = "\n\tOnly digits are accepted."
            instructions += "\n\tEnter '0' to exit."
            instructions += "\n\n\tSelect Day -> "

            option = int(input(instructions).strip())
            
            if option == 0:
                break

            elif option < 0 or option > len(WEEKDAYS):
                print(f"\n\tOnly option 1 - {len(WEEKDAYS)} are accepted.")
                short_pause()

            else:
                # Because WEEKDAYS index starts at 0.
                selected_day = WEEKDAYS[option - 1]
                selected_day_food_dict = food_dict.get(selected_day)
                
                add_delete_edit_menu(selected_day, selected_day_food_dict)

        except ValueError:
            print(f"\n\tOnly digits are accepted.")
            short_pause()
       
def admin_menu(username):
    while True:
        clear_screen()
        print_header(f"\tAdmin console.\n\tProceed with caution.")

        print(f"\tWelcome {username}.\n")
        print("\t1. Edit food name|price.")
        print("\t2. Shutdown server.")

        instructions = "\n\tEnter '0' to exit."
        instructions += "\n\tOnly accepts digits."
        instructions += "\n\n\tOption -> "

        try:
            option = int(input(instructions).strip())

            if option == 0:
                break

            elif option == 1:
                edit_food()

            elif option == 2:
                shutdown_server()
                       
            else:
                print(f"\n\t{option} is invalid.")
                short_pause()
        
        except KeyboardInterrupt:
            print("\n\n\tInterrupted by \"CTRL + C\"")
            print("\tLogging out.")
            short_pause()
            break

        except ValueError:
            print(f"\n\tOnly accepts digits.")
            short_pause()

def login_menu():
    while True:
        clear_screen()
        print_header("\tLogin.")

        instructions = "\tFor username, only alphabets are accepted."
        instructions += "\n\tAbove rule does not apply for password.\n"
        
        print(instructions)

        try:
            username = input("\tUsername -> ").lower().strip()

            regex = r"^[A-Za-z]*$"
            passed_regex = re.match(regex, username)

            # Passed regex, username not empty.
            if passed_regex and username != "":
                password = input("\tPassword -> ")

                if password != "":
                    hashed_password = md5(password.encode()).hexdigest()

                    client_socket = connect_to_server()
                    client_socket.connect((HOST, PORT))

                    client_socket.send(b'login')
                    server_reply = client_socket.recv(255).decode()

                    if server_reply == "ok":
                        username_and_password = str([username, hashed_password]).encode()
                        client_socket.send(username_and_password)

                        # authentication_data = str([login, username, is_admin, discount_rate]).encode()
                        authentication_data = eval(client_socket.recv(255).decode())
                        client_socket.close()

                        login_ok = authentication_data[0]
                        username = authentication_data[1]
                        is_admin = authentication_data[2]
                        discount_rate = authentication_data[3]

                        if login_ok:
                            print("\n\tLogging you in.")
                            short_pause()
                            
                            if is_admin == "yes":
                                admin_menu(username)
                            else:
                                user_menu(username, discount_rate)

                        else:
                            print("\n\tEither your username or password is wrong.")
                            short_pause()
                    
                else:
                    print("\n\tPassword must be not empty.")
                    short_pause()

            else:
                print("\n\tOnly accepts alphabets and no spaces for username.")
                print("\tCheck your input again.")
                short_pause()

        except KeyboardInterrupt:
            print("\n\n\tInterrupted by \"CTRL + C\"")
            print("\tExiting program.")
            short_pause()
            break
                
        except Exception as error:
            print(f"\n\t{error}")
            sys.exit(1)
        
try:
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    DAY_OF_THE_WEEK = day_name[date.today().weekday()]
    
    HOST = "127.0.0.1"
    PORT = 4444

    food_dict = convert_data_to_nested_dict(download_data())
    todays_food_dict = food_dict.get(DAY_OF_THE_WEEK)
    food_cart_dict = dict()

    login_menu()

except Exception as error:
    print(error)
    sys.exit(1)