from flask import Flask, render_template
import os
import sys

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
food_dict = dict()

app = Flask(__name__)

@app.route('/')
def home():
    url_list = list()

    for day_of_the_week in WEEKDAYS:
        url_list.append(f"http://localhost/{day_of_the_week}")

    return render_template('index.html', url_list = url_list, weekdays = WEEKDAYS)

@app.route('/view/<day_of_the_week>')
def view(day_of_the_week):
    food_menu = food_dict.get(day_of_the_week) 

    # food_menu will be None if key(day_of_the_week) is non-existent
    if food_menu: # True 
        return render_template('data.html', food_data = food_menu, day_of_the_week = day_of_the_week)
    else:
        return render_template('404.html', message = f'/view/{day_of_the_week} was not found.')

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

if __name__ == '__main__':
    food_dict = load_data_to_nested_dict()
    app.run(debug = True)
