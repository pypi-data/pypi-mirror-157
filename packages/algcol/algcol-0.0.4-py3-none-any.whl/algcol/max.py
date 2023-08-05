def find_max(input_list):
    max = input_list[0]
    for element in input_list:
        if (element > max):
            max = element
    return max