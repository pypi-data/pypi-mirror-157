import datetime
import logging
import asyncio
from typing import Iterable, Callable
from threading import Thread, Event, RLock

import schedule

logger = logging.getLogger("schedule")

_thread_pool: Iterable[Thread] = []


async def schedule_job(job_cb: Callable):
    return job_cb()


class threaded_job(schedule.Job):
    def run(self):
        """
        Run the job and immediately reschedule it.
        If the job's deadline is reached (configured using .until()), the job is not
        run and CancelJob is returned immediately. If the next scheduled run exceeds
        the job's deadline, CancelJob is returned after the execution. In this latter
        case CancelJob takes priority over any other returned value.

        :return: The return value returned by the `job_func`, or CancelJob if the job's
                 deadline is reached.

        """
        if self._is_overdue(datetime.datetime.now()):
            logger.debug("Cancelling job %s", self)
            return schedule.CancelJob

        logger.debug("Running job %s", self)
        ret = await schedule_job(self.job_func)
        self.last_run = datetime.datetime.now()
        self._schedule_next_run()

        if self._is_overdue(self.next_run):
            logger.debug("Cancelling job %s", self)
            return schedule.CancelJob
        return ret


def register_schedule():
    schedule.Job = threaded_job


__all__ = [
    register_schedule.__name__
]
