from cs50 import get_float

while True:
    change = get_float("Change: ")
    if change > 0:
        break

twofive = 0
ten = 0
five = 0
one = 0
change = round(change * 100)

while change > 0:
    if change >= 25:
        change -= 25
        twofive += 1
    elif change >= 10:
        change -= 10
        ten += 1
    elif change >= 5:
        change -= 5
        five += 1
    else:
        change -= 1
        one += 1

result = twofive + ten + five + one
print(result)
