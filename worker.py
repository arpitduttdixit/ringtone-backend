# worker.py
import logging
from redis import Redis
from rq import Worker, Queue
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD =  os.getenv("REDIS_PASSWORD")

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