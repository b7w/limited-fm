# -*- coding: utf-8 -*-

import logging
import time

from Queue import Queue
from threading import Thread

logger = logging.getLogger( __name__ )

class Worker( Thread ):
    """
    Worker Thread. Take Queue and log.
    Queue takes (func, args, kargs).
    """
    def __init__(self, tasks, logger):
        super( Worker, self ).__init__()
        self.tasks = tasks
        self.active = True
        self.logger = logger
        self.daemon = True

    def run(self):
        while self.active:
            item = self.tasks.get( )
            if item != None:
                try:
                    func, args, kargs = item
                    func( *args, **kargs )
                except Exception as e:
                    self.logger.error( e )
                    self.tasks.task_done( )
            else:
                time.sleep(10)


class ThreadPool( Thread ):
    """
    ThreadPool.
    """
    def __init__(self, num_threads, logger):
        super( ThreadPool, self ).__init__()
        self.active = True
        self.threads = []
        self.tasks = Queue( )
        self.logger = logger
        self.daemon = True
        for _ in range( num_threads ):
            self.threads.append( Worker( self.tasks, self.logger ) )
        self.start()

    def add_task(self, func, *args, **kargs):
        self.tasks.put( (func, args, kargs) )

    def run(self):
        for th in self.threads:
            time.sleep( 5 )
            th.start( )
        while self.active:
            time.sleep( 10 )


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
            return cls.instance


class Tasks(object):
    """
    Singleton Thread container.
    if main tread stop, all data will be lost!!
    """
    __metaclass__ = Singleton
    pool = ThreadPool( 2, logger )