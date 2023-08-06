import mysql.connector



# create table
def create_table(): 
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="user",
        password="password",
        database="mydatabase"
        )
        cnn = mydb.cursor()
        check_table = check_table_exist(cnn)
        if not check_table:
            cnn.execute("CREATE TABLE customers (MessageId VARCHAR(255), ReceiptHandle VARCHAR(255), MD5OfBody VARCHAR(255), Body VARCHAR(255))")
        
        return True            
    except:
        return False


# check if table exist
def check_table_exist(conection):
    stmt = "SHOW TABLES LIKE 'customers'"
    conection.execute(stmt)
    result = conection.fetchone()
    if result:
        return True
    else:
        return False

        
#insert record in the database
def insert_record(records):
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="user",
        password="password",
        database="mydatabase"
        )
        cnn = mydb.cursor()
        for record in records.get('Messages'):
            messageId = record.get('MessageId')
            receiptHandle = record.get('ReceiptHandle')
            mD5OfBody = record.get('MD5OfBody')
            body = record.get('Body')
            # will add check for duplicate
            sql = "INSERT INTO customers (MessageId, ReceiptHandle, MD5OfBody, Body) VALUES (%s, %s, %s, %s)"
            val = (messageId , receiptHandle, mD5OfBody, body)
            cnn.execute(sql, val)
            mydb.commit()
        return receiptHandle
    except:
        return ""



# select data from database
def select_record():
    mydb = mysql.connector.connect(
    host="localhost",
    user="user",
    password="password",
    database="mydatabase"
    )
    cnn = mydb.cursor()
    sql = "SELECT * FROM customers"
    cnn.execute(sql)
    myresult = cnn.fetchall()
    return myresult


#delete all records
def delete_record():
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="user",
        password="password",
        database="mydatabase"
        )
        cnn = mydb.cursor()
        sql = "DELETE FROM customers"
        cnn.execute(sql)
        mydb.commit()
        return True            
    except:
        return False
