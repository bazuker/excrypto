import sqlite3


class ExecutedOrdersHistoryDatabase:
    def __init__(self, name):
        # create a local database
        self.__conn = sqlite3.connect(name + '.db')
        self.__c = self.__conn.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS executed_orders (type text, time datetime, id text, status text, price real, amount real, filled real)''')

    def execute_sql(self, sql):
        try:
            self.__c.execute(sql)
            return self.__c.fetchall()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))
        return None

    def add_entry(self, order_type, entry):
        if entry is None:
            return
        tup = (order_type, entry.datetime, entry.id, entry.status, entry.price, entry.amount, entry.filled)
        try:
            self.__c.execute('INSERT INTO stocks VALUES(?, ?,?,?,?,?,?)', tup)
            self.__conn.commit()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))
