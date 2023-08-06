import typer
from src.stack_queue import receive_message, get_all_data, delete_record


app = typer.Typer()

def main():
    app()

@app.command(short_help='Consume n messages from SQS context')
def consume(count: int = typer.Option(...)):    
    if(count < 1 or type(count)==str):
        print("Count option must be a number and must be greater than 1")
    else:
        
        response = receive_message(count)
        if (response):
            print("Data successfully cosumed and inserted into database")
        else:
            print("Failed to consume data, genrate message")


@app.command(short_help='Show all from SQS context')
def show():
    try:
        
        response = get_all_data()
        if(len(response)==0):
            print("No record found on the database")
        for x in response:
            print(f"MessageId: {x[0]}")
            print(f"Body: {x[3]}")
            print(" ")

    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("No data, generate message and consume data")



@app.command(short_help='Clear all consumed messages from database')
def clear():
    try:
        response = delete_record()
        if(response):
            print("record successfully deleted")
        else:
            print("No message to delete record, generate message")
    except:
        print("No message to delete record, generate message")


