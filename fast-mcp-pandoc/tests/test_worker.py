"""
Test suite for the pandoc worker implementation.
"""

import asyncio
import os
from typing import Callable, List

import pytest
import pytest_asyncio

from fast_mcp_pandoc.models import ConversionRequest
from fast_mcp_pandoc.worker import ConversionTask, WorkerPool


@pytest.fixture
def worker_pool() -> WorkerPool:
    """Create a test worker pool."""
    return WorkerPool(max_workers=2)


@pytest_asyncio.fixture
async def cleanup_worker_pool(worker_pool: WorkerPool) -> None:
    """Cleanup worker pool after tests."""
    yield
    await worker_pool.shutdown()


@pytest.fixture
def test_conversion_request(test_markdown_content: str) -> ConversionRequest:
    """Create a test conversion request."""
    return ConversionRequest(
        contents=test_markdown_content,
        input_format="markdown",
        output_format="html"
    )


@pytest.mark.asyncio
async def test_worker_pool_submit_task(
    worker_pool: WorkerPool,
    cleanup_worker_pool: None,
    test_conversion_request: ConversionRequest
) -> None:
    """Test submitting a task to the worker pool."""
    # Create a future to track task completion
    result_future = asyncio.Future()
    progress_updates: List[str] = []
    
    # Define a callback that records progress and sets the future
    def progress_callback(task_id: str, percentage: int, message: str) -> None:
        progress_updates.append(f"{percentage}%: {message}")
        if percentage == 100:
            result_future.set_result(message)
        elif percentage == -1:
            result_future.set_exception(ValueError(message))
    
    # Create and submit the task
    task = ConversionTask(
        request=test_conversion_request,
        task_id="test-task-123",
        progress_callback=progress_callback
    )
    
    await worker_pool.submit_task(task)
    
    # Wait for the task to complete with timeout
    try:
        result = await asyncio.wait_for(result_future, timeout=10.0)
        assert result is not None
        assert "<h1" in result  # Check for HTML tags in result
        
        # Verify progress updates
        assert len(progress_updates) >= 3  # At least starting, converting, complete
        assert any("0%" in update for update in progress_updates)
        assert any("100%" in update for update in progress_updates)
    except asyncio.TimeoutError:
        pytest.fail("Worker task timed out")


@pytest.mark.asyncio
async def test_worker_pool_error_handling(
    worker_pool: WorkerPool,
    cleanup_worker_pool: None
) -> None:
    """Test worker pool error handling with invalid request."""
    # Create a future to track task completion
    result_future = asyncio.Future()
    progress_updates: List[str] = []
    
    # Define a callback that records progress and sets the future
    def progress_callback(task_id: str, percentage: int, message: str) -> None:
        progress_updates.append(f"{percentage}%: {message}")
        if percentage == 100:
            result_future.set_result(message)
        elif percentage == -1:
            result_future.set_exception(ValueError(message))
    
    # Create an invalid request (unsupported format)
    invalid_request = ConversionRequest(
        contents="# Test",
        input_format="markdown",
        output_format="unsupported_format"
    )
    
    # Create and submit the task
    task = ConversionTask(
        request=invalid_request,
        task_id="test-error-task",
        progress_callback=progress_callback
    )
    
    await worker_pool.submit_task(task)
    
    # Wait for the task to fail with timeout
    with pytest.raises(ValueError):
        await asyncio.wait_for(result_future, timeout=10.0)
    
    # Verify error update was recorded
    assert any("-1%" in update for update in progress_updates)


@pytest.mark.asyncio
async def test_worker_pool_concurrent_tasks(
    worker_pool: WorkerPool,
    cleanup_worker_pool: None,
    test_conversion_request: ConversionRequest
) -> None:
    """Test worker pool handling multiple concurrent tasks."""
    # Create futures to track task completion
    result_futures = [asyncio.Future() for _ in range(3)]
    
    # Define callbacks that set the futures
    def create_callback(future_index: int) -> Callable:
        def callback(task_id: str, percentage: int, message: str) -> None:
            if percentage == 100:
                result_futures[future_index].set_result(message)
            elif percentage == -1:
                result_futures[future_index].set_exception(ValueError(message))
        return callback
    
    # Create and submit multiple tasks
    tasks = []
    for i in range(3):
        task = ConversionTask(
            request=test_conversion_request,
            task_id=f"concurrent-task-{i}",
            progress_callback=create_callback(i)
        )
        tasks.append(task)
        await worker_pool.submit_task(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*result_futures, return_exceptions=True)
    
    # Verify all tasks completed successfully
    for result in results:
        assert isinstance(result, str)
        assert "<h1" in result  # Check for HTML tags
