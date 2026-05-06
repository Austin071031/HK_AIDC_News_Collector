import asyncio
import logging
from typing import AsyncGenerator

# Global queue for SSE clients
# We initialize it as None so it can be created inside the correct event loop
log_queue = None

class QueueLogHandler(logging.Handler):
    def emit(self, record):
        global log_queue
        if log_queue is None:
            return
            
        msg = self.format(record)
        try:
            # We must put the message into the queue using the event loop that created it
            # But from a synchronous logger call, we might not be in that loop
            # Try to get the running loop
            loop = asyncio.get_running_loop()
            log_queue.put_nowait(msg)
        except RuntimeError:
            # If we are not in an event loop (e.g. running in a thread pool),
            # we need to schedule it in the loop that owns the queue.
            # However, asyncio.Queue is not thread-safe.
            # For simplicity in this app, we'll assume the worker and SSE are in the same loop
            # or we just ignore logs that come from outside the loop.
            pass

def setup_log_stream():
    global log_queue
    if log_queue is None:
        try:
            # Only create the queue if we are in an event loop
            asyncio.get_running_loop()
            log_queue = asyncio.Queue()
        except RuntimeError:
            pass
        
    handler = QueueLogHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt="%H:%M:%S"))
    handler.setLevel(logging.INFO)
    
    # Attach to root logger or hk_aidc_news logger
    logger = logging.getLogger("hk_aidc_news")
    if not any(isinstance(h, QueueLogHandler) for h in logger.handlers):
        logger.addHandler(handler)

async def log_generator() -> AsyncGenerator[str, None]:
    global log_queue
    if log_queue is None:
        log_queue = asyncio.Queue()
        
    while True:
        try:
            # Using timeout to ensure we don't hang indefinitely if the client disconnects
            msg = await asyncio.wait_for(log_queue.get(), timeout=2.0)
            yield f"data: {msg}\n\n"
        except asyncio.TimeoutError:
            # Keep-alive
            yield f": keep-alive\n\n"
        except asyncio.CancelledError:
            break
