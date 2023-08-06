import sys
import time
import threading
import logging as log


class ThreadRetriesExceededException(Exception):
    pass


class ThreadExceptionNotRetryable(Exception):
    pass


class ThreadPlusPlus(threading.Thread):
    def __init__(self, target=None, args=None, retry_on=None, max_retry=0):
        threading.Thread.__init__(self, target=target, args=args)
        self._return = None
        self._exception = None
        self._retry = 1
        self._retry_on = retry_on
        self._max_retry = max_retry

    def start(self):
        if self._started.is_set():
            if self._exception is not None:
                exc_type, exc_obj, exc_trace = self._exception

                if self._retry_on is None:
                    raise ThreadExceptionNotRetryable(
                        f"Thread specified no recoverable exceptions"
                    )
                elif exc_type not in self._retry_on:
                    raise ThreadExceptionNotRetryable(
                        f"Exception {exc_type} not in allowed list"
                    )
                elif self._max_retry < 0:
                    raise ThreadExceptionNotRetryable(
                        f"Thread specified no retries allowed"
                    )
                elif self._retry >= self._max_retry:
                    raise ThreadRetriesExceededException(
                        f"Thread has exceeded retry limit of {self._max_retry}"
                    )
                else:
                    # If none of the retry blockers occur, reset the internal state
                    self._retry += 1
                    self._return = None
                    self._exception = None
                    self._started = threading.Event()
                    self._is_stopped = False

        super().start()

    def run(self):
        try:
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self._exception = sys.exc_info()

    def join(self, timeout=None):
        super().join(timeout=timeout)

        if self._exception is not None:
            exc_type, exc_obj, exc_trace = self._exception
            raise exc_obj
        else:
            return self._return

    @property
    def state(self):
        assert self._initialized, "Thread.__init__() was not called"
        state = "waiting"
        if self._started.is_set():
            state = "started"
        self.is_alive()
        if self._is_stopped:
            state = "stopped"
        return state

    @property
    def result(self):
        if self._exception is not None:
            exc_type, exc_obj, exc_trace = self._exception
            return exc_obj
        else:
            return self._return

    @property
    def retryable(self):
        """
        Returns whether the thread can be retried based on the current state,
        the exception thrown and the retry count.
        :return: True if the thread can be retried
        """
        if self._started.is_set():
            if self._exception is not None:
                exc_type, exc_obj, exc_trace = self._exception

                if self._retry_on is None:
                    return False
                elif exc_type not in self._retry_on:
                    return False
                elif self._max_retry < 0:
                    return False
                elif self._retry >= self._max_retry:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False


class ThreadPool(object):
    def __init__(self, max_concurrency=None):
        self.pool = []
        self.max = max_concurrency
        self.log = log.info

    def __filter_pool__(self, state):
        return [thread for thread in self.pool if thread.state == state]

    @property
    def waiting(self):
        return self.__filter_pool__("waiting")

    @property
    def started(self):
        return self.__filter_pool__("started")

    @property
    def stopped(self):
        return self.__filter_pool__("stopped")

    @property
    def unfinished(self):
        return self.waiting + self.started

    @property
    def exceptions(self):
        return [thread for thread in self.pool if isinstance(thread.result, Exception)]

    @property
    def retryable(self):
        return [thread for thread in self.pool if thread.retryable]

    @property
    def started_count(self):
        return len(self.__filter_pool__("started"))

    @property
    def has_waiting(self):
        if self.waiting:
            return True
        else:
            return False

    @property
    def has_started(self):
        if self.started:
            return True
        else:
            return False

    @property
    def has_stopped(self):
        if self.stopped:
            return True
        else:
            return False

    @property
    def has_unfinished(self):
        if self.unfinished:
            return True
        else:
            return False

    @property
    def has_exceptions(self):
        if self.exceptions:
            return True
        else:
            return False

    @property
    def results(self):
        if not self.has_unfinished:
            return [thread.result for thread in self.pool]
        else:
            raise RuntimeError(
                f"The ThreadPool has {len(self.unfinished)} unfinished threads"
            )

    @property
    def ready(self):
        return self.max is None or self.started_count < self.max

    def add(self, task):
        assert isinstance(
            task, ThreadPlusPlus
        ), "ThreadPool expects tasks to be type ThreadPlusPlus"

        self.pool.append(task)

    def start(self):
        if self.max is None:
            limit_str = f"with no limit"
        else:
            limit_str = f"up to {self.max}"

        self.log(f"Starting {len(self.pool)} threads in ThreadPool, {limit_str}")

        while self.waiting:
            if self.ready:
                self.log(
                    f"ThreadPool: {self.started_count} threads running, starting the next"
                )
                self.waiting[0].start()
            else:
                time.sleep(0.1)

        self.log("ThreadPool: All threads successfully started")

    def retry(self):
        if self.retryable:
            self.log(f"ThreadPool: Retrying {len(self.retryable)} threads")
            while self.retryable or self.unfinished:
                if self.retryable and self.ready:
                    self.log(
                        f"ThreadPool: {self.started_count} threads running, starting the next of {len(self.retryable)} retryable threads"
                    )
                    t = self.retryable[0]
                    t.start()

                    self.log(t.state)
                    # from .qa import breakpoint
                    # breakpoint()
                else:
                    time.sleep(0.1)

    def join(self):
        self.log(
            f"ThreadPool: {len(self.stopped)} threads complete, waiting for {len(self.started)} remaining threads"
        )
        while self.has_unfinished:
            time.sleep(0.1)

        self.retry()

        self.log(f"ThreadPool: All threads have completed, gathering results")
        if self.has_exceptions:
            self.log(f"ThreadPool: {len(self.exceptions)} threads yielded exceptions")
            for ex in self.exceptions:
                try:
                    raise ex.result
                except:
                    log.exception("ThreadPool Exception:")

            raise RuntimeError(
                f"The ThreadPool raised {len(self.exceptions)} exceptions out of {len(self.pool)} threads"
            )
        else:
            return self.results
