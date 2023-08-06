from get_auth import current_request

get_order = current_request.get_order()
file = open('order_line.txt', 'w')
file.write(str(get_order))
print(f'Orders Line: {get_order}')
