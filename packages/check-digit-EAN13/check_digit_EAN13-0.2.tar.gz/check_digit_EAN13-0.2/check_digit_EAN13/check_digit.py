def get_check_digit(number):
    number = str(number)
    str_len = len(number)
    if str_len < 12:
        return "sorry, please enter 12 digits"
    if not number.isdigit():
        return "please enter 12 digit numbers"
    number = number[:12]
    digits = [int(x) for x in str(number)]
    even_sum,odd_sum = 0,0
    for index,x in enumerate(digits):
        index = index+1
        if (index % 2) == 0:
            even_sum = even_sum + x
        else:
            odd_sum = odd_sum + x
    added = (even_sum * 3) + odd_sum
    reminder = added %  10
    if reminder == 0:
        check_digit = 0
    else:
        check_digit = 10 - reminder
    result = str(number) + str(check_digit)
    return result