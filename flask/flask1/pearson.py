import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

from scipy.stats import pearsonr

# connect to Oracle database and use query to get data
connection = oracledb.connect(user="zhouheng", password='9LKAvkfciKbMMu2S2DGrWftg', host="oracle.cise.ufl.edu",
                              port=1521, sid="orcl")
cursor = connection.cursor()

year = 2022
type1 = 'BCOUSD'
type2 = 'WTIUSD'

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
""".format(  year, type1, type2 )


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
plt.title('Pearson correlation {0}/{1} for year {2}'.format(type1, type2, year))

plt.show() 



