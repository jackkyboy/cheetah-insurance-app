# /Users/apichet/Downloads/cheetah-insurance-app/backend/kafka_subscriber/main.py
from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'insurance-query-group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'PLAINTEXT'
}

consumer = Consumer(conf)
consumer.subscribe(['insurance.query.result'])

print("📡 Listening to Kafka topic: insurance.query.result")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"❌ Kafka error: {msg.error()}")
        else:
            print("✅ Message received:")
            print(msg.value().decode('utf-8'))
except KeyboardInterrupt:
    print("🛑 Stopped.")
finally:
    consumer.close()
