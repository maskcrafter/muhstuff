dict_of_numbers = {
    "list1" : [2, 2, 3, 4],
    "list2" : [2, 3, 4, 5],
    "list3" : [2, 2, 2, 1, 1, 1, 3, 3, 3, 3],
    "list4" : [3, 5, 5, 5, 6, 6, 6, 6, 6, 2, 2]
}

def determine_lucky(mylist):
    lucky = -1

    for i in mylist:
        value = mylist.count(i)

        if value > 1 and value > lucky:
            lucky = value

    if lucky != -1:
        myset = set(mylist)

        for i in myset:
            if mylist.count(i) == lucky:
                lucky = i

    return(lucky)

for k in dict_of_numbers:
    print(f"Lucky number -> {determine_lucky(dict_of_numbers.get(k))}")