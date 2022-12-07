from datetime import datetime
import re
import inquirer
from sqlalchemy import create_engine
from prettytable import PrettyTable

engine = create_engine("mysql+pymysql://root@localhost/hotel")

def main_menu():
    print('## Main menu ##')
    main_menu_questions = inquirer.prompt([inquirer.List(name='menu', message='Choose an option', choices=['Register account', 'Remove account', 'Book a room', 'Check booking'])])
    if main_menu_questions['menu'] == 'Register account':
        register_menu()
    elif main_menu_questions['menu'] == 'Book a room':
        booking_menu()
    elif main_menu_questions['menu'] == 'Check booking':
        room_menu()

def register_menu():
    name_prompt = inquirer.prompt([inquirer.Text(name='name', message='Enter your name', validate=lambda _, x: x.isalpha())])
    with engine.connect() as conn:
        try:
            conn.execute(f"INSERT INTO customers (name) VALUES ('{name_prompt['name']}')")
        except:
            print('Account already exists.')
            main_menu()
    print('Account created.')
    main_menu()

def booking_menu():
    rooms = []
    with engine.connect() as conn:
        result = conn.execute('SELECT * FROM rooms WHERE id NOT IN (SELECT room_id FROM bookings WHERE start_date <= CURRENT_TIMESTAMP AND end_date >= CURRENT_TIMESTAMP)')
        for room in result:
            rooms.append({'id': room.id, 'is_double': room.is_double})

    table = PrettyTable()
    table.field_names = ['Room ID', 'Single/Double']
    for room in rooms:
        if room['is_double'] == 1:
            table.add_row([room['id'], 'Double'])
        else:
            table.add_row([room['id'], 'Single'])
    print('## Available rooms ##')
    print('100 SEK per person per night')
    print(table)

    name_prompt = inquirer.prompt([inquirer.Text(name='name', message='Enter your name', validate=lambda _, x: x.isalpha())])
    with engine.connect() as conn:
        customers = conn.execute(f'SELECT * FROM customers WHERE name = "{name_prompt["name"]}"')
        customer_id = 0
        for customer in customers:
            customer_id = customer.id
            break
        if customer_id == 0:
            print('Account not found.')
            booking_menu()
        
    booking_answers = inquirer.prompt([
            inquirer.Text(name='id', message="Enter desired room's ID", validate=lambda _, x: re.match('\d', x)),
            inquirer.Text(name='amount', message='Enter amount of guests', validate=lambda _, x: re.match('\d', x)),
            inquirer.Text(name='start', message='Enter desired start date (YYYY/m/d)', validate=lambda _, x: re.match('\d+/\d+/\d+', x)),
            inquirer.Text(name='end', message='Enter desired end date (YYYY/m/d)', validate=lambda _, x: re.match('\d+/\d+/\d+', x))
        ])
    start_date = datetime.strptime(booking_answers['start'], '%Y/%m/%d')
    end_date = datetime.strptime(booking_answers['end'], '%Y/%m/%d')
    print(start_date, end_date)
    delta = end_date - start_date
    price = int(booking_answers['amount']) * 100 * delta.days

    pay_now = inquirer.prompt([inquirer.List(name='answer', message=f"The price will be {price} SEK. Would you like to pay now? (Bookings will be cancelled if not paid after 10 days from creation)", choices=['Yes', 'No'])])
    if pay_now['answer'] == 'Yes':
        is_paid = 1
    else:
        is_paid = 0

    with engine.connect() as conn:
        conn.execute(f"INSERT INTO bookings (customer_id, room_id, number_of_people, start_date, end_date, price, is_paid) VALUES ({customer_id}, {booking_answers['id']}, {booking_answers['amount']}, '{booking_answers['start']}', '{booking_answers['end']}', {price}, {is_paid})")
    print('Room successfully booked.')
    main_menu()

def room_menu():
    pass

main_menu()