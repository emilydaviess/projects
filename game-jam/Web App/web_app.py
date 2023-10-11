import sqlite3
from sqlite3 import Error

conn = sqlite3.connect('employee.db') #created employee.db file in directory 
 

#Create cursor which allows us to execute SQL commands 
c = conn.cursor()

#We want an employee_records table
#c.execute("""CREATE TABLE employee_records (
#		first text, 
#		last text, 
#		pay integer)""")


#c.execute("""INSERT INTO employee_records VALUES ('Corey', 'Schafer', 50000)""") #Inset records into table! - commenting out not to re-run and duplicate. 

c.execute(""" SELECT * FROM employee_records """)
print(c.fetchall())

conn.commit() #commit changes
conn.close() #close connection


