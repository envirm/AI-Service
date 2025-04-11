import redis

def init_redis_connection(host='localhost', port=6379, db=0):

    try:
        redis_client = redis.StrictRedis(host=host, port=port, db=db)
        redis_client.ping()
        print("Connected to Redis")
        return redis_client
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return None
def publish_message_R(redis_client, channel, message):
    try:
        redis_client.publish(channel, message)
        print(f"Published message: {message} to channel: {channel}")
    except redis.RedisError as e:
        print(f"Failed to publish message: {e}")
def subscribe_message(redis_client, channel):

    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    print(f"Subscribed to channel: {channel}")

    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                print(f"Received message from channel '{message['channel']}': {message['data']}")
    except redis.RedisError as e:
        print(f"Failed to subscribe to channel: {e}")

