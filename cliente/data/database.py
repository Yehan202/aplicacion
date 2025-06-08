import mysql.connector

database = mysql.connector.connect(
    host='localhost',
    port=6033,
    ssl_disabled=True,
    user='root',
    password='root',
    database='productos'  
)