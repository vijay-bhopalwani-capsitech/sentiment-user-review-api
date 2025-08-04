import asyncio
import json
from aio_pika import connect_robust, IncomingMessage, Message
from app import SentimentInput, analyze_review  # adjust import if needed

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672"
INPUT_QUEUE = "review_jobs"
OUTPUT_QUEUE = "review_results"

async def main():
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    input_queue = await channel.declare_queue(INPUT_QUEUE, durable=True)
    output_exchange = channel.default_exchange

    async def process_message(message: IncomingMessage):
        async with message.process():
            payload = json.loads(message.body.decode())
            print("Received message from queue:", payload)

            sentiment_input = SentimentInput(**payload)
            result = analyze_review(sentiment_input)

            # Attach original _id if exists for tracking
            result["_id"] = payload.get("_id")

            print("Processed Result:", result)

            # Send to review_results queue
            await output_exchange.publish(
                Message(
                    body=json.dumps(result).encode(),
                    content_type="application/json",
                    delivery_mode=2,  # persistent
                ),
                routing_key=OUTPUT_QUEUE
            )
            print("Published result to queue:", OUTPUT_QUEUE)

    await input_queue.consume(process_message)
    print("Worker started and consuming...")

    try:
        await asyncio.Future()  # Keeps the loop running forever
    except asyncio.CancelledError:
        print("Worker stopped.")

if __name__ == "__main__":
    asyncio.run(main())
