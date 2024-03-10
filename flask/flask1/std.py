import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

from scipy.stats import pearsonr


# connect to Oracle database and use query to get data
connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
cursor = connection.cursor()




def get_std( year = 2022, type1 = 'BCOUSD' ) : 

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

""".format(  year, type1)


    result_sql = [row for row in cursor.execute(sql)]

    temp = np.array(result_sql) 
    return temp

result = get_std() 

print(result)
import matplotlib.pyplot as plt


year = 2022
type1 = 'BCOUSD'

fig,ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.set_ylabel(' fluctuation rate' )
ax2.set_ylabel(' price')

ax1.set_xlabel('Month (blue for fluctuation rate, red for price)')

ax1.plot( np.arange(1,13) , result[:,1], 'D-', lw = 2, color = 'blue' )
ax2.plot( np.arange(1,13) , result[:,0], 'D-', lw = 2,color='red' )

plt.title('Hourly fluctuation rate vs Price of {0} for year {1}'.format(type1, year))

plt.show()


