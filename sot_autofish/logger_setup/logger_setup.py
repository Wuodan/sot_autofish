"""
Logger Setup Module

This module provides a custom logger class `LoggerSetup` for enhanced logging.
It supports dynamic logger names based on the calling module or file and
includes automatic traceback information for error and critical logs.

Classes:
    LoggerSetup: A custom logger that configures dynamic names and traceback inclusion.
"""

import inspect
import logging
import os
import sys
import traceback
from typing import Optional


class LoggerSetup(logging.Logger):
    """
    A custom logger class with enhanced functionality.

    Features:
        - Automatically determines the logger name based on the calling module or file.
        - Provides separate formatting for error logs (with traceback location) and other logs.
        - Automatically includes traceback details for error and critical logs.
    """

    def __init__(self, log_level: Optional[str] = None):
        """
        Initialize the LoggerSetup instance.

        Args:
            log_level (Optional[str]): The log level to use. Defaults to the `LOG_LEVEL`
                                       environment variable, `GLOBAL_LOG_LEVEL`, or NOTSET.
        """
        # Get the name of the calling module
        caller_frame = inspect.stack()[1]
        module = inspect.getmodule(caller_frame[0])

        # Use module's name, or fallback to filename (if `__main__` detected)
        if module and module.__name__ != "__main__":
            logger_name = module.__name__
        else:
            # Get the file path of the caller
            file_path = os.path.relpath(caller_frame.filename)
            # Replace the file separators with dots and remove the `.py` extension
            logger_name = file_path.replace(os.path.sep, ".").replace('.py', '')

        # Initialize the base Logger with the determined name
        super().__init__(logger_name)

        # Dynamically resolve the log level
        resolved_log_level = (
            log_level
            or os.getenv("LOG_LEVEL")
            or self._get_global_log_level()
            or "NOTSET"
        )
        self.setLevel(resolved_log_level.upper())

        # Create console handler for stdout with specific log level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)

        # Custom filter to apply the correct formatter based on log level
        standard_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        error_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s [in %(pathname)s:%(lineno)d]'
        )

        class LevelBasedFormatter(logging.Filter):  # pylint: disable=too-few-public-methods
            """
            A filter that assigns different formatters based on log level.
            """
            def filter(self, record):
                if record.levelno == logging.ERROR:
                    console_handler.setFormatter(error_formatter)
                else:
                    console_handler.setFormatter(standard_formatter)
                return True

        # Attach the filter to the handler
        console_handler.addFilter(LevelBasedFormatter())

        # Clear existing handlers to avoid duplicates and add the new handler
        if not self.hasHandlers():
            self.addHandler(console_handler)

    def error(self, msg, *args, exc_info=True, **kwargs):
        """
        Log an error message, automatically including traceback details.

        Args:
            msg (str): The error message to log.
            exc_info (bool): Whether to include exception information. Defaults to True.
            *args: Additional positional arguments for the logger.
            **kwargs: Additional keyword arguments for the logger.
        """
        msg = self.add_traceback(exc_info, msg)
        super().error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, exc_info=True, **kwargs):
        """
        Log a critical message, automatically including traceback details.

        Args:
            msg (str): The critical message to log.
            exc_info (bool): Whether to include exception information. Defaults to True.
            *args: Additional positional arguments for the logger.
            **kwargs: Additional keyword arguments for the logger.
        """
        msg = self.add_traceback(exc_info, msg)
        super().critical(msg, *args, exc_info=exc_info, **kwargs)

    @staticmethod
    def add_traceback(exc_info, msg):
        """
        Add traceback information to the log message if available.

        Args:
            exc_info (bool): Whether to include exception information.
            msg (str): The original log message.

        Returns:
            str: The log message with traceback details appended, if available.
        """
        if exc_info:
            # Capture the full traceback and use the last entry for accurate line info
            _, _, exc_traceback = sys.exc_info()
            if exc_traceback:
                tb = traceback.extract_tb(exc_traceback)
                if tb:
                    filename, lineno, _, _ = tb[-1]
                    # Append the traceback location to the message
                    msg = f"{msg} [in {filename}:{lineno}]"
        return msg

    @staticmethod
    def _get_global_log_level() -> Optional[str]:
        """
        Dynamically retrieve the global `GLOBAL_LOG_LEVEL` if defined in any importing module.

        Returns:
            Optional[str]: The value of `GLOBAL_LOG_LEVEL`, or None if not defined.
        """
        # Check if GLOBAL_LOG_LEVEL exists in globals() of any module
        for module in sys.modules.values():
            if module and hasattr(module, "GLOBAL_LOG_LEVEL"):
                return getattr(module, "GLOBAL_LOG_LEVEL")
        return None
