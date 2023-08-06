
import boto3
from src.stack_database import create_table, insert_record, select_record, delete_record


#recieve message
def receive_message(count: int):        
    try:
        for x in range(count):
            queue_url = get_queue_url()
            sqs_client = boto3.client("sqs", endpoint_url='http://localhost:4576')
            response = sqs_client.receive_message(
                QueueUrl= queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
            )
            check_insert = save_record(response)
            if (len(check_insert)):
                delete_message(check_insert)
        
        return True        
    except:
        return False


#get the queue url
def get_queue_url():
    sqs_client = boto3.client("sqs", endpoint_url='http://localhost:4576')
    response = sqs_client.get_queue_url(
        QueueName="test-queue",
    )
    return response["QueueUrl"]

#save database
def save_record(records):

    check_table = create_table()   
    if (check_table):
        response = insert_record(records) 
        if(len(response)):
            return response          
    else:
        return ""

# delete queue
def delete_message(receipt_handle):
    queue_url = get_queue_url()
    sqs_client = boto3.client("sqs", endpoint_url='http://localhost:4576')
    response = sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )

#get all record from databe
def get_all_data():

    response = select_record()
    return response



#delete al message from databse
def delete_record():

    check_table_delete = delete_record()
    if check_table_delete:
        return True
    else:
        return False


