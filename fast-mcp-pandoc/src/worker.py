"""
Worker module for handling pandoc conversion processes.

This module provides a worker pool for processing document conversion tasks
asynchronously with progress updates via callbacks.
"""

import asyncio
import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pypandoc
from pydantic import BaseModel

from .models import ConversionRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("pandoc-worker")


@dataclass
class ConversionTask:
    """Represents a document conversion task."""
    request: ConversionRequest
    task_id: str
    progress_callback: Callable[[str, int, str], None]


class WorkerPool:
    """
    A pool of workers for processing document conversion tasks.
    
    This class manages a thread pool to handle document conversion tasks
    asynchronously while providing progress updates.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the worker pool.
        
        Args:
            max_workers: Maximum number of concurrent worker threads.
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, asyncio.Future] = {}
        logger.info(f"Worker pool initialized with {max_workers} workers")
    
    async def submit_task(self, task: ConversionTask) -> None:
        """
        Submit a conversion task to the worker pool.
        
        Args:
            task: The conversion task to process.
        """
        logger.info(f"Submitting task {task.task_id}")
        
        # Create a future for this task
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            self.executor,
            self._process_conversion,
            task
        )
        self.tasks[task.task_id] = future
        
        # Set up cleanup when the future completes
        future.add_done_callback(
            lambda f: self._task_done(task.task_id, f)
        )
    
    def _process_conversion(self, task: ConversionTask) -> str:
        """
        Process a document conversion task.
        
        Args:
            task: The conversion task to process.
            
        Returns:
            The conversion result or output file path.
            
        Raises:
            ValueError: If there is an error during conversion.
        """
        request = task.request
        task_id = task.task_id
        progress_callback = task.progress_callback
        
        try:
            # Update progress: Starting
            progress_callback(task_id, 0, "Starting conversion process")
            
            # Prepare extra arguments for pandoc
            extra_args = []
            
            # Configure PDF-specific options if needed
            if request.output_format == "pdf":
                extra_args.extend([
                    "--pdf-engine=xelatex",
                    "-V", "geometry:margin=1in"
                ])
            
            # Update progress: Preparing
            progress_callback(task_id, 25, "Preparing document for conversion")
            
            # Case 1: Convert from file to file
            if request.input_file and request.output_file:
                if not os.path.exists(request.input_file):
                    raise ValueError(f"Input file not found: {request.input_file}")
                
                # Ensure output directory exists
                output_dir = os.path.dirname(request.output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Update progress: Converting
                progress_callback(task_id, 50, f"Converting {request.input_file} to {request.output_format}")
                
                pypandoc.convert_file(
                    request.input_file,
                    request.output_format,
                    outputfile=request.output_file,
                    extra_args=extra_args
                )
                
                # Update progress: Finalizing
                progress_callback(task_id, 75, "Finalizing conversion")
                
                result = f"Content successfully converted and saved to: {request.output_file}"
                
            # Case 2: Convert from file to string
            elif request.input_file:
                if not os.path.exists(request.input_file):
                    raise ValueError(f"Input file not found: {request.input_file}")
                
                # Update progress: Converting
                progress_callback(task_id, 50, f"Converting {request.input_file} to {request.output_format}")
                
                result = pypandoc.convert_file(
                    request.input_file,
                    request.output_format,
                    extra_args=extra_args
                )
                
                # Update progress: Finalizing
                progress_callback(task_id, 75, "Finalizing conversion")
                
            # Case 3: Convert from string to file
            elif request.contents and request.output_file:
                # Create a temporary file for the input content
                with tempfile.NamedTemporaryFile(mode="w", suffix=f".{request.input_format}", delete=False) as temp:
                    temp.write(request.contents)
                    temp_path = temp.name
                
                try:
                    # Ensure output directory exists
                    output_dir = os.path.dirname(request.output_file)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    # Update progress: Converting
                    progress_callback(task_id, 50, f"Converting content to {request.output_format}")
                    
                    pypandoc.convert_file(
                        temp_path,
                        request.output_format,
                        outputfile=request.output_file,
                        extra_args=extra_args
                    )
                    
                    # Update progress: Finalizing
                    progress_callback(task_id, 75, "Finalizing conversion")
                    
                    result = f"Content successfully converted and saved to: {request.output_file}"
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
            # Case 4: Convert from string to string
            else:
                # Update progress: Converting
                progress_callback(task_id, 50, f"Converting content to {request.output_format}")
                
                result = pypandoc.convert_text(
                    request.contents,
                    request.output_format,
                    format=request.input_format,
                    extra_args=extra_args
                )
                
                # Update progress: Finalizing
                progress_callback(task_id, 75, "Finalizing conversion")
            
            # Update progress: Complete
            progress_callback(task_id, 100, "Conversion complete")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in task {task_id}: {str(e)}")
            # Report the error through the callback
            progress_callback(task_id, -1, f"Error: {str(e)}")
            raise ValueError(f"Error during conversion: {str(e)}")
    
    def _task_done(self, task_id: str, future: asyncio.Future) -> None:
        """
        Handle task completion and cleanup.
        
        Args:
            task_id: The ID of the completed task.
            future: The completed future object.
        """
        # Remove the task from the active tasks dictionary
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Task {task_id} completed and removed from pool")
        
        # Check for exceptions
        if future.exception():
            logger.error(f"Task {task_id} failed with error: {future.exception()}")
    
    async def shutdown(self) -> None:
        """Shutdown the worker pool and wait for all tasks to complete."""
        logger.info("Shutting down worker pool")
        # Cancel all pending tasks
        for task_id, future in self.tasks.items():
            if not future.done():
                future.cancel()
        
        # Shutdown the executor
        self.executor.shutdown(wait=True)
        logger.info("Worker pool shutdown complete")


# Global worker pool instance
worker_pool = WorkerPool()
