"""Utilities for asyncio-friendly file handling."""
from prometheus.aiofiles.threadpool import open
from prometheus.aiofiles import os

__version__ = "0.5.0.dev0"

__all__ = ['open', 'os']
