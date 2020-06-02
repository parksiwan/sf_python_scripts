from database import CursorFromConnectionPool

''' need to refactor '''


class STPackingList:

    def __init__(self, dispatch_date, product_type, customer, sf_code, product_name, qty, unit, arrival_date):
        self.dispatch_date = dispatch_date
        self.product_type = product_type
        self.customer = customer
        self.sf_code = sf_code
        self.product_name = product_name
        self.qty = qty
        self.unit = unit
        self.arrival_date = arrival_date

    def __repr__(self):
        return "<{} : {} ({}) {} {}>".format(self.customer, self.sf_code, self.product_name, self.qty, self.dispatch_date)

    def save_to_db(self):
        # This is creating a new connection pool every time! Very expensive...
        with CursorFromConnectionPool() as cursor:
            cursor.execute('INSERT INTO sushi_train_packinglist (dispatch_date, product_type, customer, sf_code, product_name, qty, unit, arrival_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                            (self.dispatch_date, self.product_type, self.customer, self.sf_code, self.product_name, self.qty, self.unit, self.arrival_date))
    '''
    @classmethod
    def load_from_db_by_email(cls, email):
        with CursorFromConnectionPool() as cursor:
            # Note the (email,) to make it a tuple!
            cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
            user_data = cursor.fetchone()
            return cls(email=user_data[1], first_name=user_data[2], last_name=user_data[3], id=user_data[0])
    '''
