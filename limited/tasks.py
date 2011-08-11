# -*- coding: utf-8 -*-

import logging
import time

from Queue import Queue
from threading import Thread
from limited.utils import Singleton

logger = logging.getLogger( __name__ )
SLEEP = 10
SLEEP_AT_START = 5

class Worker( Thread ):
    """
    Worker Thread. Take Queue and log.
    Queue takes (func, args, kargs).
    """

    def __init__(self, tasks, logger):
        super( Worker, self ).__init__( )
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
                    self.logger.debug( "Worker run " + func.__module__ + '.' + func.__name__ )
                except Exception as e:
                    self.logger.error( e )
                    self.tasks.task_done( )
            else:
                time.sleep( SLEEP )


class ThreadPool( Thread ):
    """
    ThreadPool.
    """

    def __init__(self, num_threads, logger):
        super( ThreadPool, self ).__init__( )
        self.active = True
        self.threads = []
        self.schedules = []
        self.tasks = Queue( )
        self.logger = logger
        self.daemon = True
        self.logger.error( 'Start ThreadPool' )
        for _ in range( num_threads ):
            self.threads.append( Worker( self.tasks, self.logger ) )
        self.start( )

    def add_task(self, func, *args, **kargs):
        self.tasks.put( (func, args, kargs) )

    def add_schedule(self, period, func, *args, **kargs):
        self.logger.error( 'add_schedule ' )
        sh = ScheduleTask( period, func, *args, **kargs  )
        self.schedules.append( sh )

    def run(self):
        for th in self.threads:
            time.sleep( SLEEP_AT_START )
            th.start( )
        while self.active:
            for item in self.schedules:
                if item.is_ready( ) == True:
                    item.next( )
                    self.tasks.put( item.task )
            time.sleep( SLEEP )


class ScheduleTask( object ):
    def __init__(self, period, func, *args, **kargs ):
        self.period = period + SLEEP
        self.task = (func, args, kargs)
        self.time = int( time.time( ) ) + self.period

    def next(self):
        self.time = int( time.time( ) ) + self.period

    def is_ready(self):
        delta = int( time.time( ) ) - self.time
        if abs( delta ) <= SLEEP:
            return True
        return False


class Tasks( object ):
    """
    Singleton Thread container.
    if main tread stop, all data will be lost!!
    """
    __metaclass__ = Singleton
    pool = ThreadPool( 2, logger )

    @classmethod
    def add_task(self, func, *args, **kargs):
        self.pool.add_task( func, *args, **kargs )