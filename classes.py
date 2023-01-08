from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root@localhost/hotel")

class Customer:
    def __init__(self, name: str):
        with engine.connect() as conn:
            customer_query = conn.execute(f"SELECT * FROM customers WHERE name = '{name}'")
            reservation_query = conn.execute(f"SELECT reservations.id, reservations.room_id, reservations.amount_of_guests, reservations.price, reservations.is_paid, reservations.start_date, reservations.end_date FROM reservations INNER JOIN customers ON reservations.customer_id = customers.id WHERE customers.name = '{name}'")
        for row in customer_query:
            id = row.id
        reservations = []
        for row in reservation_query:
            reservation = {'id': row.id, 'room_id': row.room_id, 'amount_of_guests': row.amount_of_guests, 'price': row.price, 'is_paid': bool(row.is_paid), 'start_date': row.start_date, 'end_date': row.end_date}
            reservations.append(reservation)

        self.__Id = id
        self.__Name = name
        self.__Reservations = reservations

    def get_id(self):
        return self.__Id

    def get_name(self):
        return self.__Name

    def get_reservations(self):
        return self.__Reservations

    def add_reservation(self, room_id, price, is_paid, start_date, end_date):
        with engine.connect() as conn:
            conn.execute(f"")

    def delete(self):
        with engine.connect() as conn:
            conn.execute(f"DELETE FROM customers WHERE id = {self.get_id()}")