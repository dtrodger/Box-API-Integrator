from __future__ import annotations
import concurrent.futures
from typing import Callable, List


def thread_pool_executor(
    task: Callable, tasks_args: List, max_workers: int = 15
) -> List:
    """
    Sets up a thread pool executor, sends tasks into the executor and returns the results
    """

    # Setup a thread pool for concurrent http requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

        # Get a list of each task's Future obj (like Promise in Node.js)
        task_futures = [executor.submit(task, *task_args) for task_args in tasks_args]

    # Set each futures results as a list item as it completes for return
    return [
        [complete_task_future.result()]
        for complete_task_future in concurrent.futures.as_completed(task_futures)
    ]
