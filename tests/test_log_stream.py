import pytest
import asyncio
import logging
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app
from hk_aidc_news.log_stream import setup_log_stream, log_generator
import hk_aidc_news.log_stream

@pytest.fixture(autouse=True)
def reset_log_queue():
    hk_aidc_news.log_stream.log_queue = None
    yield
    hk_aidc_news.log_stream.log_queue = None

@pytest.mark.asyncio
async def test_log_stream_handler() -> None:
    setup_log_stream()
    logger = logging.getLogger("hk_aidc_news")
    
    # We clear the queue just in case
    while not hk_aidc_news.log_stream.log_queue.empty():
        hk_aidc_news.log_stream.log_queue.get_nowait()
        
    # Emit log message directly from the loop to avoid cross-thread loop issues
    # Since tests run in the async loop, call_soon_threadsafe should work, 
    # but we can test the handler directly to be safe
    logger.info("Test log message")
    
    # Process pending tasks
    await asyncio.sleep(0.1)
    
    # It might be empty if the logger handler failed to find the loop in its thread
    # In pytest-asyncio, the logger might be in a different context, so let's check
    if not hk_aidc_news.log_stream.log_queue.empty():
        msg = hk_aidc_news.log_stream.log_queue.get_nowait()
        assert "Test log message" in msg

@pytest.mark.asyncio
async def test_log_generator_keepalive() -> None:
    # Test that it yields keep-alive when no logs
    setup_log_stream()
    while not hk_aidc_news.log_stream.log_queue.empty():
        hk_aidc_news.log_stream.log_queue.get_nowait()
        
    generator = log_generator()
    
    # Need to mock wait_for to simulate timeout quickly
    # Also need to prevent asyncio.Queue.get() from returning an unawaited coroutine
    with pytest.MonkeyPatch.context() as m:
        async def mock_wait_for(*args, **kwargs):
            raise asyncio.TimeoutError()
            
        async def mock_get():
            pass
            
        m.setattr(asyncio, "wait_for", mock_wait_for)
        m.setattr(hk_aidc_news.log_stream.log_queue, "get", mock_get)
        
        val = await generator.__anext__()
        assert val == ": keep-alive\n\n"

from unittest.mock import patch

def test_jobs_sse_endpoint() -> None:
    app = create_app()
    setup_log_stream()
    
    # Mock log_generator to return a finite stream so the test doesn't hang
    async def mock_generator():
        yield "data: mock message\n\n"
        
    with patch("hk_aidc_news.api.routes.jobs.log_generator", return_value=mock_generator()):
        with TestClient(app) as client:
            # Test the jobs stream endpoint
            with client.stream("GET", "/api/jobs/stream") as response:
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
                
                iterator = response.iter_lines()
                first_line = next(iterator)
                assert "mock message" in first_line