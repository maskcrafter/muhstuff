function populate_food_name_and_food_price(day_of_the_week, food_name, food_price) {
    day_of_the_week_text_box = document.getElementById("day_of_the_week_text_box");

    old_food_name_text_box = document.getElementById("old_food_name_text_box");
    old_food_price_num_box = document.getElementById("old_food_price_num_box");

    day_of_the_week_text_box.value = day_of_the_week;

    old_food_name_text_box.value = food_name;
    old_food_price_num_box.value = food_price;
}
