# worker.py
import logging
from redis import Redis
from rq import Worker, Queue

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection settings
REDIS_HOST = "redis-16523.c275.us-east-1-4.ec2.redns.redis-cloud.com"
REDIS_PORT = 16523
REDIS_PASSWORD = "7yasvArfia9r5ehQd8wz9QDyXRDc4zSB"

def setup_worker():
    try:
        # Set up Redis connection
        redis_conn = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=False  # Important: Set to False for job serialization
        )
        
        # Test Redis connection
        redis_conn.ping()
        logger.info("Successfully connected to Redis")
        
        # Create queue
        queue = Queue(
            'task_queue',
            connection=redis_conn,
        )
        
        # Create worker with custom settings
        worker = Worker(
            [queue],
            connection=redis_conn,
        )
        logger.info("Worker created successfully")
        
        return worker
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        worker = setup_worker()
        logger.info("Starting worker...")
        worker.work(with_scheduler=True)
    except Exception as e:
        logger.error(f"Failed to start worker: {str(e)}")
        raise