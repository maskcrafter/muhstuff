import socket
import sqlite3
import sys

from os import system, getcwd, path
from time import sleep


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

    def authenticate_user(self, username, password):
        file_exist = path.exists(self.db_filename)
        
        if file_exist:
            try:
                sqlite_connection = sqlite3.connect(self.db_filename)
                print("Connection to DB successful.")

                cursor = sqlite_connection.cursor()
                query = f"SELECT username, password, isAdmin FROM credentials where username = \"{username}\" and password = \"{password}\" limit 1"

                cursor.execute(query)
                result = cursor.fetchall()

                # Result is tuple contained in a list -> [('admin', 'password', '1')] , and that is why we need to:
                # 1. Extract the tuple -> index 0
                # 2. Convert the tuple to a list -> list()
                if len(result) > 0:
                    result = result[0]
                    result = list(result)

                return result

            except sqlite3.Error as error:
                print(f"Error while connecting to sqlite -> {error}")

            finally:
                # If sql connection exist, close the sql connection.
                if (sqlite_connection):
                    sqlite_connection.close()
                    print("Sqlite connection closed")
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
                
                elif data_received == 'login':
                    connection.send(b'ok')

                    # username_and_password[0] = user , username_and_password[1] = password
                    username_and_password = eval(connection.recv(255).decode())
                    result = self.authenticate_user(username_and_password[0], username_and_password[1])

                    # Authentication is successful.
                    if len(result) > 0:
                        login = True
                        isAdmin = int(result[2])
                        username = result[0]

                    # Authentication not successful.
                    else:
                        login = False
                        isAdmin = 0
                        username = ""

                    authentication = str([login, isAdmin, username]).encode()
                    connection.send(authentication)
                       
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

                print(f"Received connection from -> IP: {client_addr} PORT: {client_port}")

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

    filename = getcwd() + "\\sockets\\food.txt"
    db_filename = getcwd() + "\\sockets\\MyCreds.db"

    new_simple_food_server = Simple_Food_Server(ip_address, port, db_filename, filename)
    new_simple_food_server.food_server_start()

except Exception as error:
    print(f"Error -> {error}")
