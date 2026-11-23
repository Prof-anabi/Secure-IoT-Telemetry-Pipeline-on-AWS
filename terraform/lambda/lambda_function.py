import json
import os
from decimal import Decimal

import boto3

s3 = boto3.client("s3")
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])
BUCKET = os.environ["BUCKET"]
RETENTION_DAYS = 30


def _number(value, low, high):
    # bool is a subclass of int, so exclude it explicitly
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("not a number")
    if not low <= value <= high:
        raise ValueError("out of range")
    return value


def lambda_handler(event, context):
    try:
        temperature = _number(event["temperature"], -40, 80)
        humidity = _number(event["humidity"], 0, 100)
        device_id = str(event["device_id"])[:64]
        ts = int(event["ts"])  # epoch milliseconds from the IoT rule
    except (KeyError, ValueError, TypeError) as exc:
        print(f"Rejected payload: {exc}")
        return {"statusCode": 400}

    table.put_item(
        Item={
            "device_id": device_id,
            "ts": ts,
            "temperature": Decimal(str(temperature)),
            "humidity": Decimal(str(humidity)),
            "expires_at": ts // 1000 + RETENTION_DAYS * 86400,
        }
    )

    s3.put_object(
        Bucket=BUCKET,
        Key="latest-data.json",
        Body=json.dumps(
            {
                "device_id": device_id,
                "timestamp": ts,
                "temperature": temperature,
                "humidity": humidity,
            }
        ),
        ContentType="application/json",
        CacheControl="no-store",
    )
    return {"statusCode": 200}
