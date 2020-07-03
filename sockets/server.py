import socket
import sqlite3
import sys

from os import system, getcwd, path
from time import sleep
from datetime import datetime

class Server:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def clear_screen(self):
        system('cls')
   
class Login_Server(Server):
    def __init__(self, ip_address, port, db_filename):
        super().__init__(ip_address, port)
        self.db_filename = db_filename

    def create_new_user(self, new_username, new_password, is_admin, discount):
        db_file_exist = path.exists(self.db_filename)

        if db_file_exist:
            try:
                sqlite_connection = sqlite3.connect(self.db_filename)
                print("[Create new user] Connection to DB successful.")

                query = "INSERT INTO credentials (username, password, is_admin, discount) VALUES "
                query += f"(\"{new_username}\", \"{new_password}\", \"{is_admin}\", \"{discount}\")"

                cursor = sqlite_connection.cursor()
                cursor.execute(query)

                sqlite_connection.commit()
                return "ok"

            except sqlite3.Error:
                return "not ok"

            finally:
                # If sql connection exist, close the sql connection.
                if (sqlite_connection):
                    sqlite_connection.close()
                    print("[Create new user] Sqlite connection closed")
        
        else:
            print("Unable to find DB file.")
            sys.exit(1)

    def check_new_username(self, new_username):
        db_file_exist = path.exists(self.db_filename)

        if db_file_exist:
            try:
                sqlite_connection = sqlite3.connect(self.db_filename)
                print("[Check Username] Connection to DB successful.")

                cursor = sqlite_connection.cursor()

                query = f"SELECT username FROM credentials WHERE "
                query += f"username = \"{new_username}\" LIMIT 1"

                cursor.execute(query)
                result = cursor.fetchall()

                return result

            except sqlite3.Error as error:
                print(f"Error while connecting to sqlite -> {error}")

            finally:
                # If sql connection exist, close the sql connection.
                if (sqlite_connection):
                    sqlite_connection.close()
                    print("[Check Username] Sqlite connection closed")
        
        else:
            print("Unable to find DB file.")
            sys.exit(1)

    def authenticate_user(self, username, password):
        db_file_exist = path.exists(self.db_filename)
        
        if db_file_exist:
            try:
                sqlite_connection = sqlite3.connect(self.db_filename)
                print("[Authenticate] Connection to DB successful.")

                cursor = sqlite_connection.cursor()
                
                query = f"SELECT username, password, is_admin, discount FROM credentials WHERE "
                query += f"username = \"{username}\" and password = \"{password}\" LIMIT 1"

                cursor.execute(query)
                result = cursor.fetchall()
               
                return result

            except sqlite3.Error as error:
                print(f"Error while connecting to sqlite -> {error}")

            finally:
                # If sql connection exist, close the sql connection.
                if (sqlite_connection):
                    sqlite_connection.close()
                    print("[Authenticate] Sqlite connection closed")
        else:
            print("Unable to find DB file.")
            sys.exit(1)

class Simple_Food_Server(Login_Server):
    def __init__(self, ip_address, port, db_filename, filename):
        super().__init__(ip_address, port, db_filename)
        self.filename = filename

    def load_file(self):
        with open(self.filename) as f:
            foods = f.readlines()

        return foods
    
    def update_file(self, filename, food_dict):
        with open(filename, 'w+') as f:
            data = ""

            # Outer loop -> Monday to Sunday.
            for day_of_the_week in food_dict:
                day_of_the_week_food_dict = food_dict[day_of_the_week]

                # Inner loop -> Food for a particular day.
                for food_name in day_of_the_week_food_dict:
                    food_price = day_of_the_week_food_dict[food_name]
                    data += f'{day_of_the_week},{food_name},{food_price}\n'
            
            # Removes extra newlines from previous execution.
            f.write(data.strip())                    

    def handler(self, connection):
        while True:
            data_received = connection.recv(255).decode()
            
            if len(data_received) > 0:
                if data_received == 'download':
                    food_data = str(self.load_file())
                    connection.send(food_data.encode())
                
                elif data_received == 'upload':
                    connection.send(b'ok')

                    data = eval(connection.recv(2048).decode())
                    self.update_file(self.filename, data)

                elif data_received == 'check_username':
                    connection.send(b'ok')
                    
                    new_username = connection.recv(255).decode()
                    result = self.check_new_username(new_username)

                    if len(result) > 0:
                        connection.send(b'new_username_exists')

                    else:
                        connection.send(b'new_username_ok')

                        username_and_password = eval(connection.recv(255).decode())
                        new_username = username_and_password[0]
                        new_password = username_and_password[1]

                        # create_new_user(self, new_username, new_password, is_admin, discount)
                        account_creation_result = self.create_new_user(new_username, new_password, "no", "5")
                        connection.send(account_creation_result.encode())
                
                elif data_received == 'login':
                    connection.send(b'ok')

                    # username_and_password[0] = user , username_and_password[1] = password
                    username_and_password = eval(connection.recv(255).decode())
                    result = self.authenticate_user(username_and_password[0], username_and_password[1])

                    # Authentication is successful.
                    # [('admin', '21232f297a57a5a7438...e4a801fc3', 'yes', '15')]
                    if len(result) > 0:
                        authentication_result = result[0]
            
                        login = True
                        username = authentication_result[0]
                        is_admin = authentication_result[2]
                        discount_rate = float(authentication_result[3])

                    # Authentication not successful.
                    else:
                        login = False
                        username = ""
                        is_admin = "no"
                        discount_rate = 0

                    authentication_data = str([login, username, is_admin, discount_rate]).encode()
                    connection.send(authentication_data)
                       
                elif data_received == 'shutdown':
                    return data_received
           
            else:
                client_addr, client_port = connection.getpeername()
                print(f"Connection dropped -> IP: {client_addr} PORT: {client_port}")

                # Empty return -> Will execute code block in `finally :`
                return

    def food_server_start(self):
        self.clear_screen()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip_address, self.port))
        server_socket.listen()

        print("Simple Food Server started.")

        while True:
            try:
                print("Waiting for a new call at accept()")

                connection, address = server_socket.accept()
                client_addr, client_port = address

                connection_made_time = datetime.now().strftime("%H:%M:%S")            
                print(f"[{connection_made_time}] Received connection from -> IP: {client_addr} PORT: {client_port}")

                return_code = self.handler(connection)

                if return_code == 'shutdown':
                    break

            except Exception:
                print(f"Error -> {error}")

            finally:
                # To prevent blocking issues.
                connection.close()
                print(f"Closing connection -> IP: {client_addr} PORT: {client_port}")

        server_socket.close()
        print("Simple Food Server stopped.")

try:
    ip_address = "0.0.0.0"
    port = 4444

    filename = getcwd() + "\\food.txt"
    db_filename = getcwd() + "\\creds.db"

    new_simple_food_server = Simple_Food_Server(ip_address, port, db_filename, filename)
    new_simple_food_server.food_server_start()

except Exception as error:
    print(error)
