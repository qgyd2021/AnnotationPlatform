## 标注平台


```text
import sqlite3
sqlite_database_ = sqlite3.connect("sqlite.db")

sql="SELECT DISTINCT username FROM AnnotatorWorkload;"
cursor = sqlite_database_.execute(sql)
rows = cursor.fetchall()
print(rows)

sql="SELECT * FROM AnnotatorWorkload WHERE username='张妞妞';"
cursor = sqlite_database_.execute(sql)
rows = cursor.fetchall()
print(rows)


sql="UPDATE AnnotatorWorkload SET username='张妞妞' WHERE username='niuniu';"
sqlite_database_.execute(sql)
sqlite_database_.commit()



sql="SELECT * FROM AnnotatorWorkload;"
cursor = sqlite_database_.execute(sql)
rows = cursor.fetchall()
for row in rows:
    print(row)


```



