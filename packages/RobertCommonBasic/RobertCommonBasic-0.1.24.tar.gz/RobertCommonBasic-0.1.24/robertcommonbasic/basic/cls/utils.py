
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from func_timeout import func_timeout
from func_timeout.exceptions import FunctionTimedOut
from multiprocessing import Pool
from threading import Thread, Lock, Timer, Condition
from typing import Callable, Optional, Union


class Singleton(type):
    _instance_lock = Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Singleton._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


'''
#元类
class SingClass(metaclass=Singleton):
    def __init__(self):
        pass
'''


class SingleInstance(object):
    _instance_lock = Lock()
    _instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SingleInstance, '_instance'):
            with SingleInstance._instance_lock:
                if not hasattr(SingleInstance, '_instance'):
                    SingleInstance._instance = SingleInstance(*args, **kwargs)
        return SingleInstance._instance


def daemon_thread(fn: Callable) -> Callable[..., Thread]:

    @wraps(fn)
    def _wrap(*args, **kwargs) -> Thread:
        return Thread(target=fn, args=args, kwargs=kwargs, daemon=True)

    return _wrap


def function_thread(fn: Callable, daemon: bool, *args, **kwargs):
    return Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon)


def set_timeout_wrapper1(timeout):
    def inner_set_timeout_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func_timeout(timeout, func, *args, **kwargs)
            except FunctionTimedOut as e:
                raise Exception(f'func({func.__name__}) time out')
            except Exception as e:
                raise e
        return wrapper
    return inner_set_timeout_wrapper


class RepeatingTimer(Timer):

    '''
     @daemon_thread
        def thread_func():
            pass
    '''

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class SimpleTimer():

    def __init__(self):
        self.timer = None

    def is_running(self):
        return self.timer and self.timer.is_alive()

    def run(self, interval: int, function: Callable, args=None, kwargs=None):
        if self.is_running():
            if kwargs.get('force', False) is False:
                raise Exception(f"timer is running, please cancel")
            else:
                self.cancel()
        self._run_timer(interval, function, args, kwargs)

    def _run_timer(self, interval: int, function: Callable, args=None, kwargs=None):
        self.timer = Timer(interval, function, args, kwargs)
        self.timer.start()

    def cancel(self):
        if self.is_running():
            self.timer.cancel()
        self.timer = None


class ThreadPool:

    def __init__(self, pool_size: int, pool_fun: Callable, fun_params: list):
        self.pool_size = pool_size
        self.pool_fun = pool_fun
        self.fun_params = fun_params
        self.pool_cost = 0

    def run(self):
        start = time.time()
        with ThreadPoolExecutor(self.pool_size) as executor:
            futures = [executor.submit(self.pool_fun, *fun_param) for fun_param in self.fun_params]

        results = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

        self.pool_cost = '{:.3f}'.format(time.time() - start)
        return results

    def cost(self):
        return self.pool_cost


class MultiPool:

    def __init__(self, pool_size: int, pool_fun: Callable, fun_params: list):
        self.pool_size = pool_size
        self.pool_fun = pool_fun
        self.fun_params = fun_params
        self.pool_cost = 0

    def run(self):
        start = time.time()
        results = []
        with Pool(4) as p:
            p.map(self.pool_fun, self.fun_params)

            for result in p.imap_unordered(self.pool_fun, self.fun_params):
                if result is not None:
                    results.append(result)

        self.pool_cost = '{:.3f}'.format(time.time() - start)
        return results

    def cost(self):
        return self.pool_cost


class WaitQueue:

    def __init__(self, lock=None):
        self.condition = Condition(lock)
        self.values = []

    def wait(self, timeout: Union[int, float, None] = None):
        with self.condition:
            return self._wait(timeout)

    def _wait(self, timeout: Union[int, float, None] = None):
        self.condition.wait(timeout)

    def notify_all(self, value=None):
        with self.condition:
            if value is not None:
                self.values.append(value)
            self.condition.notify_all()

    def notify(self, value=None, n: int=1):
        with self.condition:
            if value is not None:
                self.values.append(value)
            self.condition.notify(n)