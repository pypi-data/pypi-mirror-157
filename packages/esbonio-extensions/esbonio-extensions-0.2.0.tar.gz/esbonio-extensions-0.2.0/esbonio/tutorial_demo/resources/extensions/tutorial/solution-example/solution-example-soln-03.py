def get_price(item: tuple) -> int:
    return item[1]

sorted(fruit, key=get_price, reverse=True)