import asyncio
import json

import duckdb
from aiokafka import AIOKafkaConsumer

REDPANDA_BROKER = "localhost:9092"
TOPIC_NAME = "roadblocks"
DB_FILE = "roadblocks_dwh.duckdb"


def init_db():
    conn = duckdb.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS roadblocks (
            id VARCHAR PRIMARY KEY,
            lat DOUBLE,
            long DOUBLE,
            status VARCHAR,
            created_at TIMESTAMP
        )
    """)
    conn.close()


async def consume_events():
    init_db()

    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=REDPANDA_BROKER,
        group_id="dwh-consumers",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    await consumer.start()
    print("Worker started. Listening for roadblock events...")

    db_conn = duckdb.connect(DB_FILE)

    try:
        async for msg in consumer:
            event = msg.value

            db_conn.execute(
                "INSERT INTO roadblocks VALUES (?, ?, ?, ?, ?)",
                (
                    event["id"],
                    event["lat"],
                    event["long"],
                    event["status"],
                    event["created_at"],
                ),
            )

    except Exception as e:
        print(f"Error in consumer: {e}")
    finally:
        await consumer.stop()
        db_conn.close()


if __name__ == "__main__":
    asyncio.run(consume_events())
