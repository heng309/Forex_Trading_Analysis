import oracledb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# WTI/USD = WEST TEXAS INTERMEDIATE in USD
# BCO/USD = BRENT CRUDE OIL in USD
# SPX/USD = S&P 500 in USD
# NSX/USD = NASDAQ 100 in USD
# UDX/USD = US DOLLAR INDEX in USD

# Query 1 - Minute Analysis
# Future and stock have negative correlation, i.e., when the stock increases, the future decreases.

def help1(table, start_date, end_date):
    # connect to Oracle database and use query to get data
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                                  port=1521, sid="orcl")
    cursor = connection.cursor()

    select = "SELECT datetime, open, high, low, close, volume FROM " \
             + table + " WHERE datetime >= " + "TIMESTAMP" + " \'" \
             + start_date + " 00:00:00.000\'" + " AND datetime < " + \
             "TIMESTAMP" + " \'" + end_date + " 00:00:00.000\'"
    result = [row for row in cursor.execute(select)]

    # transform data to DataFrame
    df = pd.DataFrame(result, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df.set_index('date', inplace=True)

    return df


def query1(tb1, tb2, start, end):
    df1 = help1(tb1, start, end)
    df2 = help1(tb2, start, end)
    df = pd.merge(df1, df2, on='date', how='inner')

    scaler = MinMaxScaler()
    df_scaler = scaler.fit_transform(df)

    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    ax1.plot(df['open_x'])
    ax1.set_title(tb1 + '-Minute')
    ax2.plot(df['open_y'])
    ax2.set_title(tb2 + '-Minute')
    ax3.plot(df_scaler[:, 0] - df_scaler[:, 5])
    ax3.set_title("Difference After Normalization")

    plt.tight_layout()
    # plt.savefig("./out_fig/" + "Minute" + tb1 + "_" + tb2 + ".jpg")
    plt.show()


# query1("BCOUSD", "SPXUSD", "2018-01-01", "2018-01-02")


# Query 2 - Daily Average
# WTI and Brent oil have a strong positive correlation.


def help2(tb1, tb2):
    # connect to Oracle database and use query to get data
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                                  port=1521, sid="orcl")
    cursor = connection.cursor()
    select = """
    With Daily_{0} as (select to_char(datetime,'yyyy-mm-dd') as daily_date, avg(open) as daily_open
    from {0}
    group by to_char(datetime,'yyyy-mm-dd')
    order by to_char(datetime,'yyyy-mm-dd')
),
Daily_{1} as (
select to_char(datetime,'yyyy-mm-dd') as daily_date, avg(open) as daily_open
    from {1}
    group by to_char(datetime,'yyyy-mm-dd')
    order by to_char(datetime,'yyyy-mm-dd')
)
select b.daily_date, b.daily_open as {0}_avg, w.daily_open as {1}_avg
from Daily_{0} b
join Daily_{1} w on w.daily_date = b.daily_date
""".format(tb1, tb2)
    result = [row for row in cursor.execute(select)]

    # transform data to DataFrame
    df = pd.DataFrame(result, columns=['date', tb1, tb2])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df


def query2(tb1, tb2):
    df = help2(tb1, tb2)
    fig, ax = plt.subplots()
    ax.plot(df[tb1], label=tb1)
    ax.plot(df[tb2], label=tb2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Average')
    ax.set_title('Comparison of Daily Average for {0} and {1}'.format(tb1, tb2))
    ax.legend()

    plt.tight_layout()
    # plt.savefig("./out_fig/" + "Daily_AVG_" + tb1 + "_" + tb2 + ".jpg")
    plt.show()


# query2("WTIUSD", "BCOUSD")


# Query 3 - Movement on High Index
# This query finds the open price of Nasdaq when US Dollar Index was above its average values.


def help3(tb1, tb2):
    # connect to Oracle database and use query to get data
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                                  port=1521, sid="orcl")
    cursor = connection.cursor()
    select = """With Daily_{0} as (select to_char(datetime,'yyyy-mm-dd') as daily_date, avg(open) as daily_open
    from {0}
    group by to_char(datetime,'yyyy-mm-dd')
    order by to_char(datetime,'yyyy-mm-dd')
),
Daily_{1} as (
select to_char(datetime,'yyyy-mm-dd') as daily_date, avg(open) as daily_open
    from {1}
    group by to_char(datetime,'yyyy-mm-dd')
    order by to_char(datetime,'yyyy-mm-dd')
)
select n.daily_date, n.daily_open as {0}_avg, d.daily_open as {1}_avg
from Daily_{0} n
join Daily_{1} d on n.daily_date = d.daily_date
where d.daily_open > (select avg(open) from {1})
order by n.daily_date asc
""".format(tb1, tb2)
    result = [row for row in cursor.execute(select)]

    # transform data to DataFrame
    df = pd.DataFrame(result, columns=['date', tb1, tb2])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df

def query3(tb1, tb2):
    df = help3(tb1, tb2)
    print(df.head())

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.plot(df[tb1], label=tb1)
    ax1.legend()
    ax1.set_title("{0} Movement on High {1} Days".format(tb1, tb2))
    ax2.plot(df[tb2], label=tb2)
    ax2.legend()

    plt.tight_layout()
    # plt.savefig("./out_fig/" + tb1 + "_on_high_" + tb2 + ".jpg")
    plt.show()


#query3("NSXUSD", "UDXUSD")