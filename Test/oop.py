food_cart = {
    "Chicken Rice": [2.50, 1],
    "Bee Hoon": [3.50, 3],
    "Mee Rebus": [2.60, 5]
}

class Cart:
    def __init__(self, food_name, food_price, food_quantity):
        self.food_name = food_name
        self.food_price = food_price
        self.food_quantity = food_quantity
    
    def total_price(self):
        total = self.food_price * self.food_quantity 
        return(total)

myfood_objects_list = []
for food_name in food_cart:
    price_and_quantity_list = food_cart.get(food_name)

    food_price = price_and_quantity_list[0]
    food_quantity = price_and_quantity_list[1]

    single_item_entry = Cart(food_name, food_price, food_quantity)
    myfood_objects_list.append(single_item_entry)

print("=" * 90)
print("CART".rjust(45))
print("=" * 90)

total_quantity = 0
total_price = 0

for single_myfood_object in myfood_objects_list:
    total_quantity += single_myfood_object.food_quantity
    total_price += single_myfood_object.total_price()

    print(f"{single_myfood_object.food_name: <30} X {single_myfood_object.food_quantity: <30} ${single_myfood_object.total_price():005.2f}")

print('-' * 90)

total_quantity = f"X {total_quantity}"
print(f"Total Quantity: {total_quantity: >18}")

total_price = f"${total_price:005.2f}"
print(f"Total Price: {total_price: >57}")