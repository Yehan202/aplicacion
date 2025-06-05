import mysql.connector

database = mysql.connector.connect(
    host='localhost',
    port=6033,
    ssl_disabled=True,
    user='root',
    password='my_secret_password',
    database='productos'  
)