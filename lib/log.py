"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

Basic log functions.

Each log entry is prefixed with the current time. Here is an example log entry:
    2018-06-12 21:51:35.347981, DEBUG, stuff goes here

Every time a 'new' caller makes a request, the new caller's first request is prefixed
by a blank line and the name of the caller. This helps keep the log file more readable.
For example:

    caller: index.py
    2018-06-12 22:16:41.260121, DEBUG, stuff goes here
    2018-06-12 22:16:43.364215, DEBUG, stuff goes here

    caller: widget.py
    2018-06-12 22:16:52.822444, DEBUG, stuff goes here
    2018-06-12 22:16:58.252852, DEBUG, stuff goes here
    2018-06-12 22:16:59.413431, DEBUG, stuff goes here

    caller: index.py
    2018-06-12 22:17:01.799004, DEBUG, stuff goes here
"""

import lib.kvpairs as kvpairs

import datetime


cfg = kvpairs.load(kvpairs.get_config_filename())
log_file = cfg['log.file']
log_stdout = cfg['log.stdout']
current_caller = ''


def pad_left(orig, pad, new_length):
    """
    Pad a string on the left side.

    Returns a padded version of the original string.
    Caveat: The max length of the pad string is 1 character. If the passed
            in pad is more than 1 character, the original string is returned.
    """
            
    if len(pad) > 1:
        return orig
        
    orig_length = len(orig)
    
    if orig_length >= new_length:
        return orig

    return (pad * (new_length - orig_length)) + orig


def create_message(caller, level, message):
    """
    Create a log message by prefixing the actual message with a date and timestamp, the calling file/function,
    and the log message level.
    :param caller: the calling file and function (try something like this: 'index.py::before_request')
    :param level: log level (debug, info, error, or alert)
    :param message: actual log message
    :return:
    """

    timestamp = datetime.datetime.now()
    out_message = str(timestamp) + ', ' + pad_left(level.upper() + ', ', ' ', 8) + caller + ',' + message

    return out_message


def debug(caller: str, message: str):
    __log(caller, 'Debug', message)


def info(caller: str, message: str):
    __log(caller, 'Info', message)


def error(caller: str, message: str):
    __log(caller, 'Error', message)


def alert(caller: str, message: str):
    __log(caller, 'Alert', message)


def __log(caller: str, level: str, message: str):

    out_message = create_message(caller, level, message)
    
    with open(log_file, "a") as f:
        f.write(out_message + "\n")
        
    if log_stdout == 'true':
        print(out_message)
