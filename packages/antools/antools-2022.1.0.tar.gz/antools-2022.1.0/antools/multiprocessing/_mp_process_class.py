# -*- coding: utf-8 -*-
"""
MULTIPROCESS CLASS
"""

# lib import
import multiprocessing as mp
import inspect
from antools.logging._logger_class import _get_mp_logger


class MultiProcess():
    """ Process used in multiprocessing subprocess. Used for logging and handling workflow.

        ...

        Attributes
        ----------
        status : str
            Process status. Options are ["OK", "FAIL", "PROCESSING"]. Default is "OK".
        error : str
            If process failed, reason for it should be held here
        data : ?
            Data for further purposes should be held here
        _started : bool
            Value True if Process has started.
        _processing : bool
            Value True if Process is active.
        _finished : bool
            Value True if Process has finished.
        _lock : object
            Lock from multiprocessing library.
        _logger : object
            New logger instance from main_logger.


        Methods
        -------
        __init__(self, lock:mp.Manager().Lock(), main_logger:object)
            Class constructor.
        get_logger(self):
            Returns Logger class for loggin in multiprocess.
        lock(self)
            Lock multiprocessing lock.
        release(self)
            Release multiprocessing lock
        finish(self, terminate_all:bool=True)
            Evaluates and finish the process.       

        Examples
        ------- 
        antools/multiprocessing/_examples
        """    

        
    STATUS_OPTIONS = ["OK", "FAIL", "PROCESSING"]

    status = "OK"
    error = None
    data = None

    _started = False
    _processing = False
    _finished = False

    _logger = None
    _lock = None


    def __init__(self, lock:object, main_logger:object):
        """ Class constructor.

        Parameters
        ----------
        lock
            Instance of multiprocess.Manager().lock() from main process
        logger
            Instance of logger from main process
        """     

        self._lock = lock
        self._process_name = inspect.stack()[1].function   
        self._logger = _get_mp_logger(main_logger=main_logger, process_name= self._process_name)   
        self._started = True
        self._processing = True
        self.status = "PROCESSING"
        self._logger.info("Process has started!")


    def __repr__(self):
        """ Representative string. """
        return f"MPProcess(name={self._process_name}, status={self.status}, _started={self._started}, _processing={self._processing}, _finished={self._finished})"

    def get_logger(self):
        "Returns Logger class for loggin in multiprocess."
        return self._logger


    def lock(self):
        """ Lock multiprocessing lock. """
        self._lock.acquire()


    def release(self):
        """ Release multiprocessing lock """
        self._lock.release()


    def finish(self, terminate_all:bool=True):
        """ Evaluates and finish the process.

        Parameters
        ----------
        terminate_all : bool
            If mistake will be found, the system will shut down.

        Returns
        ----------
        self

        """

        if self.status == "OK":
            self._logger.info("Process finished successfully!") if self.data else self._logger.warning("Process finished successfully, but returning no data!")
        elif self.status == "PROCESSING":
            self._logger.error("Process finished while still processing!", terminate=terminate_all)
        elif self.status == "FAIL":
            self.error = self.error if self.error else "UNKNOWN ERROR"
            self._logger.error(f"Process failed due to <{self.error}>!", terminate=terminate_all)
        else:
            self._logger.error(f"Process finished, however status is invalid <{self.status}>. Status must be in {self.STATUS_OPTIONS}!", terminate=terminate_all)

        self._processing = False
        self._finished = True

        return self

