import concurrent.futures
import functools
import time
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import Logger
from threading import Lock, Thread
from typing import Any, Callable, Tuple

from mb_std.date import utc_now


class ParallelTasks:
    def __init__(self, max_workers=5, timeout=None, thread_name_prefix="parallel_tasks"):
        self.max_workers = max_workers
        self.timeout = timeout
        self.thread_name_prefix = thread_name_prefix
        self.tasks: list[ParallelTasks.Task] = []
        self.exceptions: dict[str, Exception] = {}
        self.error = False
        self.timeout_error = False
        self.result: dict[str, Any] = {}

    @dataclass
    class Task:
        key: str
        func: Callable
        args: Tuple
        kwargs: dict

    def add_task(self, key: str, func: Callable, args: Tuple = (), kwargs: dict | None = None):
        if kwargs is None:
            kwargs = {}
        # noinspection PyCallByClass
        self.tasks.append(ParallelTasks.Task(key, func, args, kwargs))

    def execute(self) -> None:
        with ThreadPoolExecutor(self.max_workers, thread_name_prefix=self.thread_name_prefix) as executor:
            future_to_key = {executor.submit(task.func, *task.args, **task.kwargs): task.key for task in self.tasks}
            try:
                result_map = concurrent.futures.as_completed(future_to_key, timeout=self.timeout)
                for future in result_map:
                    key = future_to_key[future]
                    try:
                        self.result[key] = future.result()
                    except Exception as e:
                        self.error = True
                        self.exceptions[key] = e
            except concurrent.futures.TimeoutError:
                self.error = True
                self.timeout_error = True


def synchronized_parameter(arg_index=0, skip_if_locked=False):
    locks = defaultdict(Lock)

    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if skip_if_locked and locks[args[arg_index]].locked():
                return
            try:
                with locks[args[arg_index]]:
                    return func(*args, **kwargs)
            finally:
                locks.pop(args[arg_index], None)

        return wrapper

    outer.locks = locks
    outer.locked_parameters = list(locks.keys())
    return outer


class Scheduler:
    def __init__(self, log: Logger):
        self.log = log
        self.stopped = False
        self.jobs: list[Scheduler.Job] = []

    @dataclass
    class Job:
        func: Callable
        interval: int
        is_running: bool = False
        last_at: datetime = field(default_factory=utc_now)

    def add_job(self, func: Callable, interval: int):
        self.jobs.append(Scheduler.Job(func, interval))

    def _run_job(self, job: Job):
        if self.stopped:
            return
        try:
            job.func()
        except Exception as err:
            self.log.error("scheduler error:", exc_info=err)
        finally:
            job.is_running = False

    def _start(self):
        while not self.stopped:
            for j in self.jobs:
                if not j.is_running and j.last_at < utc_now() - timedelta(seconds=j.interval):
                    j.is_running = True
                    j.last_at = utc_now()
                    Thread(target=self._run_job, args=(j,)).start()
            time.sleep(0.5)

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        self.stopped = True
