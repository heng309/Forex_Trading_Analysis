import os
import base64
from io import BytesIO
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import oracledb
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr
matplotlib.use('Agg')

from flask import Flask, render_template, jsonify, session
from flask import make_response,redirect, request
from tinydb import TinyDB, Query
from flask_cors import CORS
app = Flask(__name__,template_folder='template')
app.config['SECRET_KEY'] = 'hello,world!' 
CORS(app)

#Database
def get_data_num(connection, table_name):
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
    cursor = connection.cursor()
    sql = """
    select count(*) from {0} 
    """ .format(table_name)
    result_sql = [row for row in cursor.execute(sql) ]
    return result_sql[0][0]

def plot_data_info(connection, table_name):
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
    cursor = connection.cursor()
    sql = """
    select * from {0} where rownum <= 5 
    """ .format(table_name)
    result_sql = [row for row in cursor.execute(sql) ]
    return (result_sql)

@app.route('/data_info', methods=['GET'])
def handle_data_info():
    table_name = request.args.get('table_name')

    # 数据库连接和查询
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu", port=1521, sid="orcl")
    data_num = get_data_num(connection, table_name)
    temp = plot_data_info(connection, table_name)
    df = pd.DataFrame(temp, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'])

    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    ax.set_title('Total tuple number: {0} of {1}'.format(data_num, table_name))
    fig.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png', dpi=200)
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

#Query1
def help1(tb1, tb2):
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

def query1(tb1, tb2, img):
    df = help1(tb1, tb2)
    print(df.head())

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.plot(df[tb1], label=tb1)
    ax1.legend()
    ax1.set_title("{0} Movement on High {1} Days".format(tb1, tb2))
    ax2.plot(df[tb2], label=tb2)
    ax2.legend()
    plt.savefig(img, format='png')
    plt.close()

@app.route('/query1', methods=['GET'])
def handle_query1():
    tb1 = request.args.get('tb1')
    tb2 = request.args.get('tb2')

    img = BytesIO()
    query1(tb1, tb2, img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

#Query2
def query2(year, tb1, tb2, img):
    # connect to Oracle database and use query to get data
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
    cursor = connection.cursor()

    sql ="""select m1, d1, ao1, ao2 from 
(
  select m as m1, d as d1, avg(open) as ao1 from
  (
    select open, extract(month from datetime) as m,
    extract(year from datetime) as y,
    extract(day from datetime) as d  from {1}
  ) 
  where y={0:d}
  group by m,d
  order by m,d 
)
join 
(
  select m as m2, d as d2, avg(open) as ao2 from
  (
     select open, extract(month from datetime) as m,
     extract(year from datetime) as y,
     extract(day from datetime) as d  from {2}  
  ) 
  where y={0:d}
  group by m,d
  order by m,d
)
on m1 = m2 and d1 = d2
order by m1, d1 
""".format(  year, tb1, tb2 )
    
    result_sql = [row for row in cursor.execute(sql)]

    temp = np.array(result_sql) 
    result = np.zeros((12,2)) 
    for i in range(12) : 
        month = i + 1 
        data = temp[np.where( temp[:,0] == month ),2:][0]
        x, y = data[:,0], data[:,1] 
        r, p = pearsonr( x, y )  
        result[i] = r, p 
    import matplotlib.pyplot as plt 

    fig,ax1 = plt.subplots()
    #ax1.set_xticks( ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ] ) 
    ax2 = ax1.twinx()  
    ax1.set_xlabel('Month (blue for r value, red for p value)')
    ax1.set_ylabel('r value')
    ax2.set_ylabel('p value')  
    ax1.plot( np.arange(1,13) , result[:,0], 'D-', lw = 2,color='blue', label = ' r value' ) 
    ax2.plot( np.arange(1,13) , result[:,1], 'D-', lw = 2, color = 'r', label = ' p value' )
    #ax1.legend(loc='upper right')
    #ax2.legend(loc='upper right')
    plt.title('Pearson correlation {0}/{1} for year {2}'.format(tb1, tb2, year))

    plt.show() 
    plt.savefig(img, format='png')
    plt.close()

@app.route('/query2', methods=['GET'])
def handle_query2():
    tb1 = request.args.get('tb1')
    tb2 = request.args.get('tb2')
    year = request.args.get('year', type=int)

    img = BytesIO()
    query2(year, tb1, tb2, img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

#Query3
def help3(tb1, tb2):
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

def query3(tb1, tb2, img):
    df = help3(tb1, tb2)
    fig, ax = plt.subplots()
    ax.plot(df[tb1], label=tb1)
    ax.plot(df[tb2], label=tb2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Average')
    ax.set_title('Comparison of Daily Average for {0} and {1}'.format(tb1, tb2))
    ax.legend()
    plt.savefig(img, format='png')
    plt.close(fig)

@app.route('/query3', methods=['GET'])
def handle_query3():
    tb1 = request.args.get('tb1')
    tb2 = request.args.get('tb2')

    img = BytesIO()
    query3(tb1, tb2, img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

#Query4
def get_std(year, tb1):
    # connect to Oracle database and use query to get data
    connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
    cursor = connection.cursor()

    sql = """
select avg(ao), avg(std)
from
(

select m, d, h, avg(open) as ao, sqrt( avg(power(open,2)) - power(avg(open),2) )/avg(open) as std
from
(
select extract(month from datetime) as m,
     extract(day from datetime) as d,
     extract(hour from datetime) as h, 
     open from {1}
     where extract(year from datetime) = {0:d}
)
group by m, d, h
)
group by m 

""".format(year, tb1)


    result_sql = [row for row in cursor.execute(sql)]

    result_array = np.array(result_sql) 
    return result_array

def plot_data(data, tb1, year, img):
    result = get_std(year, tb1)
    fig,ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.set_ylabel(' fluctuation rate' )
    ax2.set_ylabel(' price')

    ax1.set_xlabel('Month (blue for fluctuation rate, red for price)')

    ax1.plot( np.arange(1,13) , result[:,1], 'D-', lw = 2, color = 'blue' )
    ax2.plot( np.arange(1,13) , result[:,0], 'D-', lw = 2,color='red' )

    plt.title('Hourly fluctuation rate vs Price of {0} for year {1}'.format(tb1, year))

    plt.savefig(img, format='png')
    plt.close()

@app.route('/query4', methods=['GET'])
def handle_query4():
    year = request.args.get('year', type = int)
    tb1 = request.args.get('tb1')

    data = get_std(year, tb1)
    img = BytesIO()
    plot_data(data, tb1, year, img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

#Query5
# Future and stock have negative correlation, i.e., when the stock increases, the future decreases.
def help5(table, start_date, end_date):
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

def query5(tb1, tb2, start, end, img):
    df1 = help5(tb1, start, end)
    df2 = help5(tb2, start, end)
    df = pd.merge(df1, df2, on='date', how='inner')

    scaler = MinMaxScaler()
    df_scaler = scaler.fit_transform(df)

    fig = plt.figure(figsize=(10, 6), dpi=100)
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    ax1.plot(df['open_x'])
    ax1.set_title(tb1 + '-Minute')
    ax2.plot(df['open_y'])
    ax2.set_title(tb2 + '-Minute')
    ax3.plot(df_scaler[:, 0] - df_scaler[:, 5])
    ax3.set_title("Difference After Normalization")
    plt.tight_layout(pad=3.0) 
    # ...绘制图形...
    plt.savefig(img, format='png')
    plt.close(fig)

@app.route('/query5', methods=['GET'])
def handle_query5():
    # 从请求中获取参数
    tb1 = request.args.get('tb1')
    tb2 = request.args.get('tb2')
    start = request.args.get('start')
    end = request.args.get('end')

    # 调用query5函数
    img = BytesIO()
    query5(tb1, tb2, start, end, img)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return jsonify({'plot': plot_url})

@app.route('/register')
def register():
    username = request.args.get('username').strip()  #, default = 0, type = int )
    password = request.args.get('password').strip() #, default = 0, type = int )
    db = TinyDB('./db.json')
    User = Query()
    result = db.search(User.name == username )
    
    if( len(result) > 0 ) :
        status = 'already registered'                           
    else :
        status = 'success'
        db.insert({'name': username, 'password': password})

    return jsonify({'status': status})

@app.route('/login')
def login():
    username = request.args.get('username').strip() #, default = 0, type = int )
    password = request.args.get('password').strip()  #, default = 0, type = int )
    db = TinyDB('./db.json')
    User = Query()
    result = db.search(User.name == username)
    print( result ) 
    if( len(result) > 0 and result[0]['password'] == password ) : 
        status = 'success' 
        session['username'] = username 
    else : 
        status = 'failure'  

    return jsonify({'status': status})

@app.route('/')
def index():
    resp = make_response('<p> hello world</p>')
    resp.set_cookie('somecookiename', 'I am cookie')
    return resp

if __name__ == '__main__' :
    app.run()