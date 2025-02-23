import asyncio
import time
from google.cloud import pubsub_v1


class PubSubSubscriber:
    def __init__(self, project_id: str, subscription_name: str, timeout: int = 60):
        self.subscription_name = subscription_name
        self.timeout = timeout
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription_name)

    async def pull_messages(self) -> None:
        start_time = time.time()
        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=self.callback)
        print(f'Listening for messages on {self.subscription_path}...')

        try:
            while time.time() - start_time < self.timeout:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result()

    @staticmethod
    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f'Received message: {message.data.decode("utf-8")}')
        message.ack()


if __name__ == '__main__':
    from config import project_id, subscription_name

    timeout = 10
    subscriber = PubSubSubscriber(project_id, subscription_name, timeout)
    asyncio.run(subscriber.pull_messages())
