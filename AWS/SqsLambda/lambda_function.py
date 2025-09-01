import json
import urllib.request
import os
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# InfluxDB config
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
PRECISION = os.getenv("INFLUX_PRECISION", "s")

# DynamoDB config
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")
DYNAMO_BATCH_SIZE = int(os.getenv("DYNAMO_BATCH_SIZE", "10"))

dynamodb = boto3.resource('dynamodb')
batch_buffer = []

def send_to_influx(measurement, tags, value):
    try:
        tag_str = ",".join([f"{k}={v}" for k, v in tags.items()])
        line = f"{measurement},{tag_str} value={value}"
        full_url = f"{INFLUX_URL}?org={INFLUX_ORG}&bucket={INFLUX_BUCKET}&precision={PRECISION}"
        request = urllib.request.Request(
            full_url,
            data=line.encode('utf-8'),
            headers={
                "Authorization": f"Token {INFLUX_TOKEN}",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            if response.status in (200, 204):
                print(f"✅ Influx: {measurement} {tags}={value}")
                return True
            else:
                print(f"❌ Influx: Failed {measurement} {tags}={value}, HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ Influx: Error {measurement} {tags}={value}, {e}")
        return False

def prepare_item(payload):
    """Convert payload to DynamoDB item"""
    item = {
        'deviceId': payload.get('deviceId'),
        'timestamp': payload.get('timestamp')
    }
    
    for key in ['sensor', 'value', 'status', 'location', 'topics']:
        if key in payload:
            value = payload[key]
            if isinstance(value, float):
                value = Decimal(str(value))
            item[key] = value
    return item

def write_batch_to_dynamo(items):
    if not DYNAMO_TABLE or not items:
        return True
    try:
        table = dynamodb.Table(DYNAMO_TABLE)
        with table.batch_writer(overwrite_by_pkeys=["deviceId", "timestamp"]) as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"✅ DynamoDB: Wrote {len(items)} items")
        return True
    except ClientError as e:
        print(f"❌ DynamoDB: ClientError {e}")
        return False
    except Exception as e:
        print(f"❌ DynamoDB: Error {e}")
        return False

def add_to_batch(payload):
    global batch_buffer
    batch_buffer.append(prepare_item(payload))
    if len(batch_buffer) >= DYNAMO_BATCH_SIZE:
        success = write_batch_to_dynamo(batch_buffer.copy())
        if success:
            batch_buffer.clear()
            print(f"✅ DynamoDB: Batch written, buffer cleared")
        else:
            print(f"❌ DynamoDB: Batch failed, items remain in buffer")
        return success
    else:
        print(f"🟡 DynamoDB: Buffer not full ({len(batch_buffer)}/{DYNAMO_BATCH_SIZE})")
        return None

def lambda_handler(event, context):
    processed = 0
    influx_success = 0
    
    for record in event.get("Records", []):
        try:
            payload = json.loads(record["body"])
            device_id = payload.get("deviceId")
            location = payload.get("location", "unknown")

            # Type A: sensor reading
            if "sensor" in payload and "value" in payload:
                if send_to_influx(payload["sensor"], {"deviceId": device_id, "location": location}, payload["value"]):
                    influx_success += 1
            
            # Type B: status
            elif "status" in payload:
                numeric_status = 1 if payload["status"].lower() == "online" else 0
                if send_to_influx("status", {"deviceId": device_id, "location": location}, numeric_status):
                    influx_success += 1
            
            # Type C: topics
            elif "topics" in payload:
                topic_count = len(payload["topics"])
                if send_to_influx("topic_count", {"deviceId": device_id, "location": location}, topic_count):
                    influx_success += 1
            
            # Add all payloads to DynamoDB batch
            add_to_batch(payload)
            processed += 1

        except Exception as e:
            print(f"❌ Error processing record: {e}")

    # Force flush if Lambda is about to timeout
    remaining_time = context.get_remaining_time_in_millis() if context else 0
    if remaining_time < 5000 and batch_buffer:
        success = write_batch_to_dynamo(batch_buffer.copy())
        if success:
            batch_buffer.clear()
            print("✅ DynamoDB: Buffer force-flushed successfully")
        else:
            print("❌ DynamoDB: Buffer force-flush failed")
    
    return {
        "status": "ok",
        "processed": processed,
        "influx_success": influx_success,
        "batch_buffer_size": len(batch_buffer)
    }
