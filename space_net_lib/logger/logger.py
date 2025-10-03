import logging
import sys
import os
import datetime
import colorlog

root_module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_module_dir)

from definition.path import api_data_path

class DefaultLogger(logging.Logger):
    def __init__(self, name, log_file_path, level=logging.DEBUG,
                 dump_output_to_file=True,
                 log_file_format='%(levelname)s:%(asctime)s : %(message)s',
                 stdout_output_format='%(log_color)s%(levelname)s%(reset)s:     %(message)s'):
        super(DefaultLogger, self).__init__(name, level=level)

        self.current_log_file_path = log_file_path
        self.dump_output_to_file = dump_output_to_file

        colored_formatter = colorlog.ColoredFormatter(
            stdout_output_format,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        if dump_output_to_file:
            os.makedirs(os.path.dirname(self.current_log_file_path), exist_ok=True)
            self.file_handler = logging.FileHandler(self.current_log_file_path, 'w')

        self.stdout_handler = logging.StreamHandler(sys.stdout)
        # DO NOT add self.stderr_handler to the handler list ; it will cause duplicate output when logging
        # uses any type of log method.


        if dump_output_to_file:
            self.file_handler.setFormatter(logging.Formatter(log_file_format))

        self.stdout_handler.setFormatter(colored_formatter)

        if dump_output_to_file:
            self.addHandler(self.file_handler)

        self.addHandler(self.stdout_handler)

        self.redirect()


    class LoggerWriter:
        def __init__(self, level, original_stdout):
            self.level = level
            self._buffer = ""

            self.original_stdout = original_stdout
            sys.stdout = self

        def write(self, message):
            if message.replace("\n", ""):
                self.level(message.replace("\n", ""))

        def flush(self):
            pass

    def redirect(self):
        sys.stdout = self.LoggerWriter(self.error, sys.__stdout__)
        sys.stderr = self.LoggerWriter(self.info, sys.__stderr__)
        self.info("Logger redirect standard output finished.")

    def closing(self):
        self.info("Logger closing...")

        if self.dump_output_to_file:
            self.removeHandler(self.file_handler)

            try:
                new_path = os.path.join(os.path.dirname(self.current_log_file_path),
                                        f"{str(datetime.datetime.now())}.log")

                os.rename(self.current_log_file_path, new_path)
            except OSError as e:
                print(e)