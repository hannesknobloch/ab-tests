import json
import pymysql
import os

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

def handler(event, context):
    # assume the SNS message is a single record
    sns_message = json.loads(event["Records"][0]["Sns"]["Message"])
    
    transformed_data = {
        "field1": sns_message.get("field1"),
        "field2": sns_message.get("field2")
    }

    try:
        connection = pymysql.connect(host=DB_HOST,
                                      user=DB_USER,
                                      password=DB_PASSWORD,
                                      database=DB_NAME)
        
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO my_table (field1, field2) VALUES (%s, %s)"
            cursor.execute(insert_query, (transformed_data["field1"], transformed_data["field2"]))
            connection.commit()

        print("Data stored")
    
    except Exception as e:
        print(f"Error storing data: {str(e)}")
        raise e
    
    finally:
        connection.close()

    return {
        "statusCode": 200,
        "body": json.dumps("Processed and stored AB-Test results")
    }
