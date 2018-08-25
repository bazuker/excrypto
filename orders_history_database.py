import sqlite3


class OrdersHistoryDatabase:
    def __init__(self, name):
        # create a local database
        self.__conn = sqlite3.connect(name + '.db')
        self.__c = self.__conn.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS stocks (time datetime, ex1 text, ex2 text, sym1 text, 
        sym2 text, bid real, ask real, size real, sizemul real, profit real, fallback boolean)''')

    def execute_sql(self, sql):
        try:
            self.__c.execute(sql)
            return self.__c.fetchall()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))
        return None

    def add_entries(self, entries):
        if entries is None or len(entries) < 1:
            return
        t = []
        for d in entries:
            ex1 = d.exchange1
            ex2 = d.exchange2
            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2,
                   d.bid, d.ask, d.size, d.sizemul, d.profit_rate, d.can_fallback())
            t.append(tup)
        try:
            self.__c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?,?,?)', t)
            self.__conn.commit()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))
