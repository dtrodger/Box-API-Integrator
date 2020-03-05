from __future__ import annotations
import asyncio


class ConcurrentTaskLimiter:
    def __init__(self, max_concurrent_tasks: int) -> ConcurrentTaskLimiter:
        """
        * These docstrings are copied in from 3.7s asyncio.lock.Semaphore type

        A Semaphore implementation.

        A semaphore manages an internal counter which is decremented by each
        acquire() call and incremented by each release() call. The counter
        can never go below zero; when acquire() finds that it is zero, it blocks,
        waiting until some other thread calls release().

        Semaphores also support the context management protocol.
        """
        self._concurrent_task_limiter = asyncio.Semaphore(max_concurrent_tasks)
        self._tasks = set()

    async def add_task(self, coroutine: asyncio.coroutine) -> None:
        with self._concurrent_task_limiter:
            task = asyncio.create_task(coroutine)
            task.add_done_callback(self._remove_task)
            self._tasks.add(task)

    async def gather_tasks(self) -> None:
        await asyncio.gather(*self._tasks)

    def _remove_task(self, task) -> None:
        self._tasks.remove(task)
        self._concurrent_task_limiter.release()

    async def __aenter__(self) -> ConcurrentTaskLimiter:
        return self

    def __aexit__(self, exc_type, exc, tb) -> asyncio.tasks._GatheringFuture:
        return self.gather_tasks()
