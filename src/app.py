import json
import pymysql
import os

# DB_HOST = os.environ["DB_HOST"]
# DB_USER = os.environ["DB_USERNAME"]
# DB_PASSWORD = os.environ["DB_PASSWORD"]
# DB_NAME = os.environ["DB_NAME"]

DB_HOST = "rds-db"  # Service name from docker-compose
DB_USER = "testuser"
DB_PASSWORD = "testpassword"
DB_NAME = "testdb"

def lambda_handler(event, context):
    try:
        # Extract the SNS message
        sns_record = event["Records"][0]["Sns"]
        message = json.loads(sns_record["Message"])  # Parse the SNS message content

        # Extract relevant fields
        test_id = message["test_id"]
        msg_timestamp = message["msg_timestamp"]
        variants = message["variants"]

        # Find the variant with the best CTR using max()
        best_variant = max(
            variants,
            key=lambda v: (
                (int(v["clicks"]) / int(v["views"])) if int(v["views"]) > 0 else 0
            ),
        )

        # Prepare the result
        result = {
            "id": best_variant["id"],
            "timestamp": msg_timestamp,
            "test_id": test_id,
            "views": int(best_variant["views"]),
            "clicks": int(best_variant["clicks"]),
            "ctr": round(
                (int(best_variant["clicks"]) / int(best_variant["views"])) * 100, 2
            ),
        }

        # Store the result in the database
        store_result_in_db(result)

        # Log and return the best variant
        print(f"Best variant stored in database: {result}")
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        print(f"Error processing event: {e}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


def store_result_in_db(result):
    # Connect to the database
    connection = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

    try:
        with connection.cursor() as cursor:
            # Insert the result into the database
            query = """
                INSERT INTO ab_test_results (variant_id, timestamp, test_id, views, clicks, ctr)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    result["id"],
                    result["timestamp"],
                    result["test_id"],
                    result["views"],
                    result["clicks"],
                    result["ctr"],
                ),
            )
            connection.commit()
    finally:
        connection.close()
