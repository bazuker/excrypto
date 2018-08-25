import sqlite3

import matplotlib.pyplot as plt


def quick_plot_from_sql(set1, set2, title='X/Y', xlb='X', ylb='Y'):
    # converting a set of tuples to a sorted list
    list1 = list(set1)
    list2 = list(set2)
    list1.sort(reverse=True)
    list2.sort(reverse=True)
    # plotting
    plt.title(title)
    plt.plot(list1, list2)
    plt.axis([list1[len(list1) - 1], list1[0],
              list2[len(list2) - 1], list2[0]])
    plt.xlabel(xlb)
    plt.ylabel(ylb)
    plt.show()


conn = sqlite3.connect('stocks1.db')
c = conn.cursor()
sql = "select size, sizemul from stocks where sym1='XLM'"
c.execute(sql)
result = c.fetchall()
set1, set2 = zip(*result)
quick_plot_from_sql(set1, set2)
