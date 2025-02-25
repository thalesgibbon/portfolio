import asyncio
import random
import uuid
from datetime import datetime
from google.cloud import pubsub_v1


class EventGenerator:
    def generate(self) -> dict:
        raise NotImplementedError("This method should be implemented by subclasses")


class OrderEventGenerator(EventGenerator):
    def generate(self) -> dict:
        return {
            "event_type": "order",
            "order_id": str(uuid.uuid4()),
            "customer_id": str(uuid.uuid4()),
            "order_date": datetime.utcnow().isoformat(),
            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "product_name": f"Product {random.randint(1, 100)}",
                    "quantity": random.randint(1, 10),
                    "price": round(random.uniform(10.0, 100.0), 2)
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Sample City",
                "country": "Country X"
            },
            "total_amount": round(random.uniform(50.0, 500.0), 2)
        }


class InventoryEventGenerator(EventGenerator):
    def generate(self) -> dict:
        return {
            "event_type": "inventory",
            "inventory_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(uuid.uuid4()),
            "quantity_change": random.randint(-100, 100),
            "reason": random.choice(["restock", "sale", "return", "damage"]),
            "timestamp": datetime.utcnow().isoformat()
        }


class UserActivityEventGenerator(EventGenerator):
    def generate(self) -> dict:
        return {
            "event_type": "user_activity",
            "user_id": str(uuid.uuid4()),
            "activity_type": random.choice(["login", "logout", "view_product", "add_to_cart", "remove_from_cart"]),
            "ip_address": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "user_agent": "Mozilla/5.0",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "session_id": str(uuid.uuid4()),
                "platform": random.choice(["web", "mobile", "tablet"])
            }
        }


class EventFactory:
    generators = {
        "order": OrderEventGenerator(),
        "inventory": InventoryEventGenerator(),
        "user_activity": UserActivityEventGenerator()
    }

    @staticmethod
    def get_event_generator(event_type: str) -> EventGenerator:
        generator = EventFactory.generators.get(event_type)
        if not generator:
            raise ValueError(f"Unknown event type: {event_type}")
        return generator


class PubSubPublisher:
    def __init__(self, topic_name: str, project_id: str):
        self.topic_name = topic_name
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_name)

    async def publish(self, event: dict):
        data = str(event).encode("utf-8")
        future = self.publisher.publish(self.topic_path, data=data, type=event["event_type"])
        future.result()
        print(f"Published message to {self.topic_name}: {event}")


async def generate_and_publish_events(event_type: str, messages_per_second: int, duration_seconds: int, publisher: PubSubPublisher):
    generator = EventFactory.get_event_generator(event_type)
    total_messages = messages_per_second * duration_seconds
    interval = 1 / messages_per_second

    for _ in range(total_messages):
        event = generator.generate()
        await publisher.publish(event)
        await asyncio.sleep(interval)


if __name__ == '__main__':
    from config import project_id, topic_name

    event_type = "order"  # "order", "inventory" or "user_activity"
    messages_per_second = 5
    duration_seconds = 1

    publisher = PubSubPublisher(topic_name=topic_name, project_id=project_id)

    asyncio.run(generate_and_publish_events(event_type, messages_per_second, duration_seconds, publisher))
