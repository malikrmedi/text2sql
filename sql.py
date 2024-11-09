import sqlite3


connection=sqlite3.connect("students.db")


cursor=connection.cursor()


table_info= """
Create table STUDENT(NAME VARCHAR(25) ,CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT);

"""

cursor.execute(table_info)

cursor.execute(''' Insert Into STUDENT values ('malik','math','3eme',1)''')
cursor.execute(''' Insert Into STUDENT values ('fares','math','3eme',5)''')
cursor.execute(''' Insert Into STUDENT values ('zied','svt','3eme',6)''')
cursor.execute(''' Insert Into STUDENT values ('hela','svt','bac',7)''')
cursor.execute(''' Insert Into STUDENT values ('kenza','math','bac',8)''')
cursor.execute(''' Insert Into STUDENT values ('hajer','svt','bac',18)''')
cursor.execute(''' Insert Into STUDENT values ('elias','math','3eme',15)''')
cursor.execute(''' Insert Into STUDENT values ('zakaria','math','3eme',12)''')

print("the inserted lines are ...")

data=cursor.execute('''Select * from STUDENT''')

for row in data:
    print(row)


connection.commit()
connection.close()