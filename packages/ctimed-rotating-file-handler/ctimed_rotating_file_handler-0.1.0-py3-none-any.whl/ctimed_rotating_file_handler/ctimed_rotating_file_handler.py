import os
import sys
import time
from stat import ST_CTIME
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler

platform_win = sys.platform.startswith("win")

if platform_win:
    from win32_setctime import setctime


class CTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    TimedRotatingFileHandler using ctime instead of mtime to determine rollover times.

    This subclass of TimedRotatingFileHandler uses file creation time instead of file modification time to calculate
    the next rollover time.

    It also contains a workaround for file system tunneling on Windows, which prevents new files from having new
    creation times if they have already existed a short time ago.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False,
                 atTime=None, errors=None):
        # Call parent __init__ with delay=True to make sure the file is not created at this point.
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, True, utc, atTime,
                                          errors)

        # This has already been done in the parent class using ST_MTIME.
        # Do it again using ST_CTIME and overwriting the previous result.
        if os.path.exists(filename):
            t = os.stat(filename)[ST_CTIME]
            self.rolloverAt = self.computeRollover(t)

        # This opens the file if delay=False (and does some other stuff).
        FileHandler.__init__(self, filename, 'a', encoding, delay)

    # Overwrite _open() to make sure we set the correct ctime to work around Windows file system tunneling.
    def _open(self):
        need_to_set_ctime = platform_win and not os.path.exists(self.baseFilename)
        # noinspection PyProtectedMember
        stream = super()._open()
        if need_to_set_ctime:
            setctime(self.baseFilename, time.time(), follow_symlinks=True)
        return stream
