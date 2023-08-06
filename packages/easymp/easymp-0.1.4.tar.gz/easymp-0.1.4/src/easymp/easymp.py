#!/usr/bin/python3

import functools as ft
import multiprocessing as mp
import logging
import logging.handlers
import sys
try:
    from tqdm import tqdm
    tqdm_support = True
except ModuleNotFoundError:
    tqdm_support = False



#########################################################
# Setup things to enable logging                        #
# ------------------------------                        #
#                                                       #
# Based on                                              #
# https://docs.python.org/dev/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
# 0BSD License                                          #
#########################################################
def addlogging(func):
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        if not "logger" in func.__globals__:
            func.__globals__["logger"] = logging.getLogger(
                    "%s.%s" % (func.__module__, func.__name__)
                    )
        return func(*args, **kwargs)
    return wrapper


def listener_configurer():
    root = logging.getLogger()
    h = logging.StreamHandler()
    f = logging.Formatter(
            "%(levelname)s | %(asctime)s | %(name)s | %(message)s"
            )
    h.setFormatter(f)
    root.addHandler(h)


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                # We send this as a sentinel to tell
                # the listener to quit.
                break
            logger = logging.getLogger(record.name)

            # No level or filter logic applied - just do it!
            logger.handle(record)
        except Exception:
            import sys, traceback
            print("Whoops! Problem:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue):
    # Just the one handler needed
    h = logging.handlers.QueueHandler(queue)

    root = logging.getLogger()
    root.addHandler(h)

    # send all messages, for demo;
    # no other level or filter logic applied.
    root.setLevel(logging.DEBUG)


def worker_init(queue, configurer):
    configurer(queue)


@addlogging
def parallel(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exc:
            logger.error(exc, exc_info=True)
    return wrapper


@addlogging
def execute(function, it, nprocs, chunksize=1, progress=False, total=None, progress_file=sys.stderr):
    if progress and not tqdm_support:
        logger.error("Please install 'tqdm' to use the progress feature. Disable progress.")
        progress = False
    if progress and total == None:
        logger.warning("The progress feature is most useful when the total number of elements in the iterator is specified.")
    queue = mp.Queue(-1)
    listener = mp.Process(target=listener_process, args=(queue, listener_configurer))
    listener.start()
    with mp.Pool(nprocs, initializer=worker_init, initargs=(queue, worker_configurer)) as p:
        if progress:
            p.imap_unordered(function, tqdm(it, total=total, file=progress_file), chunksize=chunksize)
        else:
            p.imap_unordered(function, it, chunksize=chunksize)
        p.close()
        p.join()
    queue.put_nowait(None)
    listener.join()
