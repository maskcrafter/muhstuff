import socket
import re
import sys

from time import sleep
from os import system, getcwd, path
from calendar import day_name
from datetime import date
from random import randint

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
        print(f"Error -> {error}")

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
        print(f"Error -> {error}")

    finally:
        client_socket.close()

def convert_data_to_nested_dict(food_list):
    temp_food_dict = {}

    for day_of_the_week in WEEKDAYS:
        food_name_and_price_dict = {}

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
        print_header(f"\t{DAY_OF_THE_WEEK}'s Menu")
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
            instructions = "\n\tEnter \"0\" to exit."
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
                        ordered_food_price = local_food_dict[food_name]
                        break

                clear_screen()
                print_header(f"\t{ordered_food_name}'s page.")

                instructions = "\tOnly digits are accepted."
                instructions += "\n\tMin digits - 1, Max digits - 2."
                instructions += "\n\n\tQuantity -> "
                
                order_quantity = input(instructions).strip()

                # https://stackoverflow.com/questions/4824942/regex-to-match-digits-of-specific-length
                regex = r"^\d{1,2}$"

                if re.match(regex, order_quantity):
                    order_quantity = int(order_quantity)

                    if order_quantity == 0:
                        print(f"\n\tYou have cancelled ordering {ordered_food_name}.")
                        short_pause()
                        break
                    
                    elif order_quantity < 0:
                        print("\n\tNegative values are not accepted.")
                    
                    else:
                        price_and_quantity_list = [ordered_food_price, order_quantity]
                        food_cart_dict[ordered_food_name] = price_and_quantity_list

                        print(f"\n\tSuccessfully added {ordered_food_name} X {order_quantity} to the cart.")
                        pause()
                        break
                
                else:
                    print("\n\tQuantity must be in digits.\n\tAdditionally check min\max digits.")

        except ValueError as error:
            print(f"\n\tInvalid option -> {error}")

        short_pause()

def search_food():
    while True:
        clear_screen()
        print_header(f"\tFood-Search Menu")

        instructions = "\tOnly alphabets and spaces are accepted."
        instructions += "\n\tEnter \"exit\" to go back to the previous menu."
        instructions += "\n\n\tSearch -> "
        
        food_to_search = input(instructions).lower().strip()

        # https://stackoverflow.com/questions/30994738/how-to-make-input-only-accept-a-z-etc
        # https://pythex.org/
        regex = r"^[A-Za-z ]*$"
        search_hits_dict = {}

        if re.match(regex, food_to_search) and food_to_search != "":
            if food_to_search == "exit":
                break
      
            for food_name in todays_food_dict:
                if food_name.lower().find(food_to_search) != -1:
                    search_hits_dict[food_name] = todays_food_dict[food_name]

            if len(search_hits_dict) > 0:
                order_food(search_hits_dict)

            else:
                print(f"\n\tSearch founds no food similar to \"{food_to_search}\".")
                short_pause()
 
        else:
            print("\n\tPlease check your input again.")
            short_pause()

def list_order():    
    global food_cart_dict

    while True:
        clear_screen()

        if len(food_cart_dict) > 0:
            print_header("\tYour order.")

            total_price = 0

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict[food_name]
                
                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity
                total_price += food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                food_price = f"${food_price:.2f}"

                print(f"\t{count}. {food_name_and_quantity.ljust(50)} {food_price}")
            
            total_price = f"${total_price:.2f}".rjust(55)
            print_header(f"\tTotal{total_price}")

            instructions = "\n\tOnly 'q', 's', 'e' are accepted."
            instructions += "\n\n\tEnter \"q\" to go back to the main menu."
            instructions += "\n\tEnter \"s\" to print out receipt."
            instructions += "\n\tEmpty \"e\" to empty cart.\n\n\tOption -> "
            
            option = input(instructions).lower().strip()
            regex = r"\w{1}"

            if re.match(regex, option):
                if option == 'q':
                    break

                elif option == 's':
                    print_receipt(RECEIPT_FILE_PATH)
                    print("\n\tSave successful.")
                    pause()
                    break

                elif option == 'e':
                    food_cart_dict.clear()
                    clear_screen()
                    print("\tEmptied food cart.")
                    pause()
                    break

                else:
                    print("\n\tInvalid option.")
                    short_pause()

            else:
                print("\n\tOnly 'q', 's', 'e' are accepted.")
                short_pause()
        
        else:
            print("\n\tFood cart is empty.")
            pause() 
            break

def print_receipt(filename):
    if len(food_cart_dict) > 0:
        with open(filename, 'w') as f:
            order_number = randint(1, 500)

            data = "Thank you for ordering from SPAM.\n"
            data += f"Order number: #{order_number}\n\n"
            data += "=" * 64
            data += "\nYour order\n"
            data += "=" * 64

            total_price = 0

            for count, food_name in enumerate(food_cart_dict, 1):
                price_and_quantity_list = food_cart_dict[food_name]

                food_price = price_and_quantity_list[0]
                food_quantity = price_and_quantity_list[1]

                food_price *= food_quantity
                total_price += food_price

                food_name_and_quantity = f"{food_name} X {food_quantity}"
                data += f"\n{count}. {food_name_and_quantity.ljust(50)} ${food_price:.2f}"

            total_price = f"${total_price:.2f}".rjust(55)

            data += "\n"
            data += "=" * 64
            data += f"\nTotal{total_price}\n"
            data += "=" * 64
            data += "\n\nPlease present this receipt at the counter.\n"
            data += f"Total amount payable -> {total_price.strip()}"

            f.write(data)
        
    else: 
        print(f"\n\tCart is empty. There is nothing to be printed.")
        pause()

def user_menu(username):
    while True:
        clear_screen()
        print_header("\tAutomated Food Menu.")
        print(f"\tWelcome {username}.\n")
        print("\t1. Display today's menu.")
        print("\t2. Search food.")
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
                list_todays_food_menu()
            
            elif option == 2:
                search_food()
           
            elif option == 3:
                list_order()

        except ValueError as error:
            print(f"\n\tPlease check your input -> {error}")
            short_pause()

def shutdown_server():
    try:
        client_socket = connect_to_server()
        client_socket.connect((HOST, PORT))
        
        client_socket.send(b'shutdown')

        print("\n\tShutdown completed.")

    except Exception as error:
        print(f"\n\tError -> {error}")

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
        instructions += "\n\tEnter \"exit\" to exit."
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

        # Passed regex, not empty, not duplicate.
        if re.match(regex, new_food_name) and new_food_name != "" and duplicate == False:
            try:
                new_food_price = float(input("\tEnter new food price -> ").strip())

                selected_day_food_dict[new_food_name] = new_food_price 
                food_dict[selected_day] = selected_day_food_dict
                food_cart_dict.clear()

                update_data()

                print(f"\n\tSuccessfully added {new_food_name} -> ${new_food_price:.2f} .")
                short_pause()

                return "added"

            except ValueError as error:
                print(f"\n\tError -> {error}")
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

    old_price = selected_day_food_dict[selected_food_name]

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
    
    except ValueError as error:
        print(f"\n\tInput is not a floating point number -> {error}")
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

        except ValueError as error:
            print(f"\n\tOnly digits are accepted -> {error}")
            short_pause()

def choose_food(selected_day_food_dict, selected_day):
    while True:
        clear_screen()
        print_header(f"\t{selected_day}'s Food Menu.")

        list_food(selected_day_food_dict)
        
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
                
                # When food name, food price have been updated, breaks loop and return to day selection to prevent stale data.
                return_code = edit_food_name_or_food_price_or_delete_food(selected_day, selected_day_food_dict, selected_food_name)

                if return_code == "updated" or return_code == "deleted":
                    return "break"

        except ValueError as error:
            print(f"\n\tOnly digits are accepted -> {error}")
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
                print("\n\tInvalid input.")
                short_pause()

        except ValueError as error:
            print(f"\n\tOnly digits are accepted. -> {error}")
            short_pause()

def edit_food():
    while True:
        clear_screen()
        print_header("\tEdit Food.")

        for count, day_of_the_week in enumerate(WEEKDAYS, 1):
            print(f"\t{count}. {day_of_the_week}")
        
        try:
            instructions = "\n\tOnly digits are accepted."
            instructions += "\n\tEnter \"0\" to exit."
            instructions += "\n\n\tSelect Day -> "

            option = int(input(instructions).strip())
            
            if option == 0:
                break

            elif option < 0 or option > len(WEEKDAYS):
                print("\n\tOnly option 1-7 are accepted.")
                short_pause()

            else:
                # Because WEEKDAYS index starts at 0.
                selected_day = WEEKDAYS[option - 1]
                selected_day_food_dict = food_dict[selected_day]
                
                add_delete_edit_menu(selected_day, selected_day_food_dict)

        except ValueError as error:
            print(f"\n\tOnly digits are accepted -> {error}")
            short_pause()
       
def admin_menu(username):
    while True:
        clear_screen()
        print_header(f"\tAdmin console.\n\tProceed with caution.")

        print(f"\tWelcome {username}.\n")
        print("\t1. Edit food name/price menu.")
        print("\t2. Shutdown server.")

        instructions = "\n\tEnter \"0\" to exit."
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
        
        except ValueError as error:
            print(f"\n\tOnly accepts digits -> {error}")
            short_pause()

def login_menu():
    while True:
        clear_screen()
        print_header("\tLogin.")

        instructions = "\tFor username, only alphabets are accepted."
        instructions += "\n\tAbove rule does not apply for password.\n"
        
        print(instructions)

        username = input("\tUsername -> ").lower().strip()
        regex = r"^[A-Za-z]*$"

        if re.match(regex, username):
            password = input("\tPassword -> ")

            if password != "":
                try:
                    client_socket = connect_to_server()
                    client_socket.connect((HOST, PORT))

                    client_socket.send(b'login')
                    server_reply = client_socket.recv(255).decode()

                    if server_reply == "ok":
                        username_and_password = str([username, password]).encode()
                        client_socket.send(username_and_password)

                        authentication_details = eval(client_socket.recv(255).decode())
                        client_socket.close()

                        login_ok = authentication_details[0]
                        is_admin = bool(authentication_details[1])
                        username = authentication_details[2]

                        if login_ok:
                            print("\n\tLogging you in.")
                            short_pause()
                            
                            if is_admin:
                                admin_menu(username)
                            else:
                                user_menu(username)

                        else:
                            print("\n\tEither your username or password is wrong.")
                
                except Exception as error:
                    print(f"\n\tError -> {error}")
                    pause()
            
            else:
                print("\n\tPasssword must not empty.")

        else:
            print("\n\tOnly accepts alphabets and no spaces for username.\n\tCheck your input again.")
        
        short_pause()

try:
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    DAY_OF_THE_WEEK = day_name[date.today().weekday()]

    RECEIPT_FILE_PATH = getcwd() + "\\order.txt"
    
    #HOST = "backend01.itflee.com"
    HOST = "127.0.0.1"
    PORT = 4444

    food_dict = convert_data_to_nested_dict(download_data())
    todays_food_dict = food_dict[DAY_OF_THE_WEEK]
    food_cart_dict = {}

    login_menu()
  
except KeyboardInterrupt as error:
    print("\n\tInterrupted by \"CTRL + C\"")
    print("\tGoodbye.")

except Exception as error:
    print(f"Error -> {error}")
