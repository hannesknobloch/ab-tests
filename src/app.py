import json
import pymysql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB_HOST = os.environ["DB_HOST"]
# DB_USER = os.environ["DB_USERNAME"]
# DB_PASSWORD = os.environ["DB_PASSWORD"]
# DB_NAME = os.environ["DB_NAME"]

DB_HOST = "rds-db"  # Service name from docker-compose
DB_USER = "testuser"
DB_PASSWORD = "testpassword"
DB_NAME = "testdb"

CTR_MARGIN = 0.20  # 20% margin

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

        # Calculate the CTR of the best variant
        best_ctr = (
            (int(best_variant["clicks"]) / int(best_variant["views"])) * 100
            if int(best_variant["views"]) > 0
            else 0
        )

        # Check if the best variant's CTR is 20% better than all other variants
        for variant in variants:
            if variant != best_variant:
                # Calculate CTR for this variant
                ctr = (
                    (int(variant["clicks"]) / int(variant["views"])) * 100
                    if int(variant["views"]) > 0
                    else 0
                )
                # Check if the best CTR is at least 20% better than this variant's CTR
                if best_ctr <= ctr * (1 + CTR_MARGIN):
                    logger.info(
                        "No winner found: Best variant does not have 20% better CTR than all other variants."
                    )
                    return {"statusCode": 200, "body": "No winner found."}

        # Prepare the result
        result = {
            "id": best_variant["id"],
            "timestamp": msg_timestamp,
            "test_id": test_id,
            "views": int(best_variant["views"]),
            "clicks": int(best_variant["clicks"]),
            "ctr": round(best_ctr, 2),
        }

        # Store the result in the database
        store_result_in_db(result)

        # Log and return the best variant
        logger.info(f"Best variant stored in database: {result}")
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        logger.error(f"Error processing event: {e}")
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
                INSERT INTO ab_test_results (variant_id, test_id, views, clicks, ctr)
                VALUES (%s, %s, %s, %s, %s)
            """
            logger.info(f"Executing query: {query} with data: {result}")
            cursor.execute(
                query,
                (
                    result["id"],
                    result["test_id"],
                    result["views"],
                    result["clicks"],
                    result["ctr"],
                ),
            )
            connection.commit()
    finally:
        connection.close()
