import boto3
import json
from datetime import datetime

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = "IOTData"
BUCKET_NAME = "iotdatas3backup"

def lambda_handler(event, context):
    # Scan the DynamoDB table
    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response['Items']

    # Convert DynamoDB format to normal JSON and remove ttl field
    cleaned_items = []
    for item in items:
        normal_item = {k: list(v.values())[0] for k, v in item.items() if k != "ttl"}
        cleaned_items.append(normal_item)

    # Date parts
    now = datetime.now()
    year_str = now.strftime("%Y")          # 2025
    month_str = now.strftime("%B")         # August
    today_str = now.strftime("%d-%m-%Y")   # 29-08-2025

    # File name
    file_name = f"{today_str}-SensorData.json"

    # Folder structure: year/month/file
    s3_key = f"{year_str}/{month_str}/{file_name}"

    # Upload to S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(cleaned_items, indent=2)
    )

    print(f"Backup written to s3://{BUCKET_NAME}/{s3_key}")
    return {"status": "success", "file": s3_key}
