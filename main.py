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
    delta = end_date - start_date
    price = int(booking_answers['amount']) * 100 * delta.days

    pay_now = inquirer.prompt([inquirer.List(name='answer', message=f"The price will be {price} SEK. Would you like to pay now? (Bookings will be cancelled if not paid after 10 days from creation)", choices=['Yes', 'No'])])
    if pay_now['answer'] == 'Yes':
        is_paid = 1
    else:
        is_paid = 0

    with engine.connect() as conn:
        conn.execute(f"INSERT INTO bookings (customer_id, room_id, number_of_people, start_date, end_date, price, is_paid) VALUES ({customer_id}, {booking_answers['id']}, {booking_answers['amount']}, '{start_date}', '{end_date}', {price}, {is_paid})")
        result = conn.execute(f"SELECT * FROM bookings WHERE customer_id = {customer_id} AND room_id = {booking_answers['id']} AND start_date = '{start_date}' AND end_date = '{end_date}'")
        for row in result:
            booking_id = row.id
    print('Room successfully booked. Your booking ID:', booking_id)
    main_menu()

def room_menu():
    table = PrettyTable()
    table.field_names = ['Room ID', '# of people', 'Price', 'Is paid', 'From', 'To']
    bookings = []
    name_prompt = inquirer.prompt([inquirer.Text(name='name', message='Please enter your name')])
    with engine.connect() as conn:
        customer_bookings = conn.execute(f"SELECT * FROM bookings INNER JOIN customers ON bookings.customer_id = customers.id WHERE customers.name = '{name_prompt['name']}'")
    for row in customer_bookings:
        bookings.append(row.room_id)
        if row.is_paid == 1:
            table.add_row([row.room_id, row.number_of_people, row.price, 'Yes', row.start_date, row.end_date])
        else:
            table.add_row([row.room_id, row.number_of_people, row.price, 'No', row.start_date, row.end_date])
    print(table)

    room_id_prompt = inquirer.prompt([inquirer.List(name='room_id', message='Select room', choices=bookings)])
    with engine.connect() as conn:
        booking = conn.execute(f"SELECT * FROM bookings INNER JOIN customers ON bookings.customer_id = customers.id WHERE customers.name = '{name_prompt['name']}' AND bookings.room_id = {room_id_prompt['room_id']}")
    for row in booking:
        start_date = row.start_date
        end_date = row.end_date
    delta = end_date - start_date
    choice_prompt = inquirer.prompt([inquirer.List(name='choice', message='Select option', choices=['Change # of people', 'Change date', 'Cancel booking'])])
    if choice_prompt['choice'] == 'Change # of people':
        people_prompt = inquirer.prompt([inquirer.Text(name='amount', message='Enter new number of people', validate=lambda _, x: re.match('\d', x))])
        price = int(people_prompt['amount']) * 100 * delta.days
        confirm_prompt = inquirer.prompt([inquirer.List(name='answer', message=f'New price will be {price}. Do you wish to continue?', choices=['Yes', 'No'])])
        if confirm_prompt['answer'] == 'Yes':
            pay_prompt = inquirer.prompt([inquirer.List(name='answer', message='Would you like to pay now?', choices=['Yes', 'No'])])
            if pay_prompt['answer'] == 'Yes':
                with engine.connect() as conn:
                    conn.execute(f"UPDATE bookings JOIN customers ON bookings.customer_id = customers.id SET bookings.number_of_people = {people_prompt['amount']}, bookings.price = {price}, bookings.is_paid = 1 WHERE customers.name = '{name_prompt['name']}' AND bookings.room_id = {room_id_prompt['room_id']}")
                print('Successfully updated booking')
            else:
                with engine.connect() as conn:
                    conn.execute(f"UPDATE bookings JOIN customers ON bookings.customer_id = customers.id SET bookings.number_of_people = {people_prompt['amount']}, bookings.price = {price}, bookings.is_paid = 0 WHERE customers.name = '{name_prompt['name']}' AND bookings.room_id = {room_id_prompt['room_id']}")
                print('Successfully updated booking')
        elif confirm_prompt['answer'] == 'No':
            main_menu()
    elif choice_prompt['choice'] == 'Change date':
        pass
    elif choice_prompt['choice'] == 'Cancel booking':
        with engine.connect() as conn:
            conn.execute(f"DELETE bookings FROM bookings INNER JOIN customers ON customers.id = bookings.customer_id WHERE customers.name = '{name_prompt['name']}' AND bookings.room_id = {room_id_prompt['room_id']}")
        print('Successfully cancelled booking.')
        main_menu()

main_menu()