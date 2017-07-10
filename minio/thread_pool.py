# -*- coding: utf-8 -*-
# Minio Python Library for Amazon S3 Compatible Cloud Storage, (C)
# 2017 Minio, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
minio.thread_pool
~~~~~~~~~~~~

This module implements a thread pool API to run several tasks
in parallel. Tasks results can also be retrieved.

:copyright: (c) 2017 by Minio, Inc.
:license: Apache 2.0, see LICENSE for more details.

"""

import sys
from threading import Thread
from .compat import queue

class Worker_py2(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks_queue, results_queue):
        Thread.__init__(self)
        self.tasks_queue = tasks_queue
        self.results_queue = results_queue
        self.daemon = True
        self.start()

    def run(self):
        fast_quit = False
        while True:
            func, args, kargs = self.tasks_queue.get()
            if not fast_quit:
                try:
                    result = func(*args, **kargs)
                    self.results_queue.put(result)
                except Exception as e:
                    print(e)
                    fast_quit = True
            # Mark this task as done, whether an exception happened or not
            self.tasks_queue.task_done()


class ThreadPool_py2:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.results_queue = queue()
        self.tasks_queue = queue(num_threads)
        for _ in range(num_threads):
            Worker_py2(self.tasks_queue, self.results_queue)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks_queue.put((func, args, kargs))

    def parallel_run(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)
        self.tasks_queue.join()

    def result(self):
        """ Return the result of all called tasks """
        return self.results_queue

import asyncio
from concurrent.futures import ThreadPoolExecutor
 
async def do_work(loop, work_queue, result_queue):
    executor = ThreadPoolExecutor()
    while not work_queue.empty():
        func, args, kargs = await work_queue.get()
        r = await loop.run_in_executor(executor, func, *args, **kargs)
        result_queue.put(r)

class ThreadPool_py3:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks_queue = asyncio.Queue()
        self.results_queue = queue()

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks_queue.put_nowait((func, args, kargs))
        
    def parallel_run(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_tasks = [asyncio.async(do_work(loop, self.tasks_queue, self.results_queue))]
        loop.run_until_complete(asyncio.wait(async_tasks))
        # loop.close()

    def result(self):
        """ Return the result of all called tasks """
        return self.results_queue
