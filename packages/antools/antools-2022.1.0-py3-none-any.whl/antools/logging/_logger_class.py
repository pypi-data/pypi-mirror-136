# -*- coding: utf-8 -*-
"""
LOGGER CLASS
"""

# lib import
import logging
import os
import sys
import getpass
import shutil
import inspect
from datetime import datetime
import attr
from attr import define, field
import multiprocessing

@define
class _Logger():
    """ Customizable Logger for tracking logs and catching unexpected errors.
    The class should be activated only separated method get_logger().

    ...

    Attributes
    ----------
    level : str, optional
        Level of the logger (default is 'INFO'). Options are ["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]
    _console_log : bool, optional
        Determines whether logging should be done to console too (default is True).
    _file_log : bool, optional
        Determines whether logging should be done to file (default is True).
    _user_name : str, optional
        Name of the user (default is '<Your user profile>').
    _folder path : str, optional
        Folder where logs will be stored (default is <CWD>/logs).
    _active : bool, optional
        If active, logger class logs messages (default is False).
    _activated : bool, optional
        If activated, log file will be created and logger becomes active (default is False).
    _logger : class, optional
        Logger class from logging library, becomes active when this class is activated (default is None).
    _main_logger : class, optional
        If multiprocessing or threrading is used, enter main instance of this class.
    _process_name : str, optional
        If multiprocessing or threading is used, process_name is has to be filled.
    _formatter
        Logger format.

    Methods
    -------
    debug(msg:str)
        Logs debug messages.
    info(msg:str)
        Logs info messages.
    warning(msg:str)
        Logs warning messages.
    critical(msg:str)
        Logs critical messages.
    error(self, msg:str, error=SystemError, terminate:bool=True)
        Logs error messages and terminates the system if wanted.
    exception(self, msg:str, error=SystemError, add_info:bool = False, terminate:bool = False)
        Logs exception messages and terminates the system if wanted.

    Examples
    ------- 
    antools/logging/_examples.py   
    """

    # init
    _level = field(default="INFO", validator=attr.validators.instance_of(str))
    _console_log = field(default=True, validator=attr.validators.instance_of(bool))
    _file_log = field(default=True, validator=attr.validators.instance_of(bool))
    _user_name = field(default=getpass.getuser(), validator=attr.validators.instance_of(str))
    _folder_path = field(default=os.path.join(os.getcwd(), "logs"), validator=attr.validators.instance_of(str))
    _main_logger = field(default=None, validator=attr.validators.instance_of(object))
    _process_name = field(default="MAIN", validator=attr.validators.instance_of(str))

    _active = field(default=False, validator=attr.validators.instance_of(bool))
    _activated = field(default=False, validator=attr.validators.instance_of(bool))
    _logger = field(default=None)
    _logger_file_path = field(default=None)

    _formatter = logging.Formatter("%(asctime)s.%(msecs)03d : %(levelname)s : %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    @_level.validator
    def _level_validator(self, attribute, value):
        """ Validates _level attribute """
        level_options = ["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]
        if value not in level_options:
            raise ValueError(f"Logger level must must have one of following values: {level_options}")


    @_active.validator
    def _active_init(self, attribute, value):
        """ Order list for when Logger is activated by user. """

        if value is True and not self._activated:
            self._logger = logging.getLogger()

            # multiprocess/threading logger inheritance
            if self._main_logger:
                if not self._process_name:
                    raise ValueError("When using main logger parameter, fill <process_name>!")

                self._level = self._main_logger._level
                self._console_log = self._main_logger._console_log
                self._file_log = self._main_logger._file_log
                self._user_name = self._main_logger._user_name
                self._folder_path = self._main_logger._folder_path
                self._logger_file_path = self._main_logger._logger_file_path

            else:
                self._process_name = "MAIN"
                now = datetime.now()
                full_path = os.path.join(self._folder_path, str(datetime.now().year), now.strftime('%B'), self._user_name)
                self._logger_file_path = os.path.join(full_path, f"{now.strftime('%B_%d_%Y_%H_%M_%S')}.log")

                # if folder does not exist, create it
                if self._file_log:
                    try:
                        os.makedirs(full_path) if not os.path.isdir(full_path) else None
                    except:
                        raise ValueError(f"{value} is not valid system path!")
                
                    # delete old logs
                    years = os.listdir(self._folder_path)
                    for year_dir in years:
                        if os.path.isdir(os.path.join(self._folder_path, year_dir)):
                            if not year_dir in [str(now.year), str(now.year - 1)]:
                                try:
                                    shutil.rmtree(os.path.join(self._folder_path, year_dir))
                                except:
                                    pass

            self._logger.setLevel(self._level)

            if self._file_log:
                fh = logging.FileHandler(self._logger_file_path, mode='a')
                fh.setFormatter(self._formatter)
                self._logger.addHandler(fh)
            
            if self._console_log:
                sh = logging.StreamHandler()
                sh.setFormatter(self._formatter)
                self._logger.addHandler(sh)

            self._replace_traceback()
            self._activated = True
            self._active = True
            self.debug("Logging has been activated!")

    # validators
    @_activated.validator
    def _activated_validator(self, attribute, value):
        """ Guards that Logger can be activated only once. """
        if self._activated and value==False:
            self._logger.warning("Activated attribute cannot be changed!")
            self._activated = True


    def debug(self, msg:str):
        """ Logs debug messages.
        
        Parameters
        ----------
        msg
            Message to be logged.

        """
        if self._active:
            self._logger.debug(self._get_msg_format() + msg)
            

    def info(self, msg:str):
        """ Logs info messages.
        
        Parameters
        ----------
        msg
            Message to be logged.
        
        """
        if self._active:
            self._logger.info(self._get_msg_format() + msg)
        

    def warning(self, msg:str):
        """ Logs warning messages.
        
        Parameters
        ----------
        msg
            Message to be logged.
        
        """

        if self._active:
            self._logger.warning(self._get_msg_format() + msg)
    
    def critical(self, msg:str):
        """ Logs critical messages.
        
        Parameters
        ----------
        msg
            Message to be logged.
        
        """     
        if self._active:
            self._logger.critical(self._get_msg_format() + msg)


    def error(self, msg:str, error=SystemError, terminate:bool = True):
        """ Logs error messages and terminates the system if wanted.
        
        Parameters
        ----------
        msg : msg
            Message to be logged.
        error : Error, optional
            ErrorType (default is SystemError).
        terminate : bool, optional
            If true, Logger will shut down process (default is True).

        """

        self._logger.error(self._get_msg_format() + msg)
        if terminate:
            # change for right traceback in VSCode
            error = SystemError if error == SystemExit else error
            raise error(msg)


    def exception(self, msg:str, error=SystemError, add_info:bool = False, terminate:bool = False):
        """ Logs exception messages and terminates the system if wanted.
        
        Parameters
        ----------
        msg : msg
            message to be logged
        error : Error, optional
            ErrorType (default is SystemError)
        add_info : bool, optional
            adds traceback to the message
        terminate : bool, optional
            if true, Logger will shut down process (default is False)

        """

        self._logger.exception(self._get_msg_format() + msg, exc_info=add_info)
        if terminate:
            add_info = True
            error = SystemError if error == SystemExit else error
            raise error(msg)

    def _get_msg_format(self) -> str:
        """ Formats logger info for logging messages. """

        if self._level == "DEBUG":
            try:
                stack = inspect.stack()[2]
                path = stack.filename
                cwd = os.getcwd()
                path = "..\\" + os.path.relpath(path, cwd) if cwd in path else path
                function = stack.function if stack.function != "<module>" else "module"
                return f"{self._process_name.upper()} : {path} : line {stack.lineno} : function <{function}>" + " : "
            except:
                return f"{self._process_name.upper()} : "

        else:
            return f"{self._process_name.upper()} : "


    def _replace_traceback(self):  
        """ Replace traceback for logging unexpected errors """

        def log_traceback_system(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
      
            self._logger.error(self._get_msg_format() + "The following error cannot be handled! \n", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = log_traceback_system 



_LOGGER = _Logger() 

def get_logger( level:str="INFO", 
                console_log:bool=True, 
                file_log:bool=True,
                user_name:str=getpass.getuser(), 
                folder_path:str=os.path.join(os.getcwd(), "logs"),
                _activate:bool = True) -> _Logger:

    """
    Returns Instance of Logger class

    Parameters
    ----------
    level : str, optional
        Level of the logger (default is 'INFO'). Options are ["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]
    console_log : bool, optional
        Determines whether logging should be done to console (default is True).
    file_log : bool, optional
        Determines whether logging should be done to file (default is True).
    user_name : str, optional
        Name of the user (default is '<Your user profile>').
    folder path : str, optional
        Folder where logs will be stored (default is <CWD>/logs).
    _activate
        !!! DO NOT CHANGE !!!

    Returns
    -------
    Instance of Logger Class

    """ 
    if _activate:
        _LOGGER._level = level
        _LOGGER._console_log = console_log
        _LOGGER._file_log = file_log
        _LOGGER._user_name = user_name
        _LOGGER._folder_path = folder_path
        _LOGGER._active = _activate

    return _LOGGER


def _get_mp_logger(main_logger:_Logger,
                    process_name:str) -> _Logger:
    """
    Returns Instance of Logger class for multiprocessing purposes

    Parameters
    ----------
    main_logger : object
        Instance of main logger
    process_name : str
        Name of the process
    Returns
    -------
    Instance of Logger Class

    """ 
    _LOGGER._main_logger = main_logger

    if not process_name:
        raise ValueError("Multiprocessing logger cannot be activated without <process_name>!")

    _LOGGER._process_name = process_name
    _LOGGER._active = True

    return _LOGGER


def _get_thread_logger(main_logger:_Logger,
                        process_name:str) -> _Logger:
    """
    Returns Instance of Logger class for threading purposes

    Parameters
    ----------
    main_logger : object
        Instance of main logger
    process_name : str
        Name of the process
    Returns
    -------
    Instance of Logger Class

    """ 
    _LOGGER._main_logger = main_logger

    if not process_name:
        raise ValueError("Multiprocessing logger cannot be activated without <process_name>!")

    _LOGGER._process_name = process_name
    _LOGGER._active = True

    return _LOGGER