# CTimedRotatingFileHandler

TimedRotatingFileHandler using `ctime` instead of `mtime` to determine rollover times.

This module provides a subclass `CTimedRotatingFileHandler` of `logging.handlers.TimedRotatingFileHandler` that uses
file creation time instead of file modification time to calculate the next rollover time.

It also contains a workaround for "file system tunneling" on Windows, which prevents new files from having new
creation times if they have already existed a short time ago.  
To be able to do this, a new dependency to `win32-setctime` is introduced (only needed if running on Windows).

## Usage Example
```py
import logging
from ctimed_rotating_file_handler import CTimedRotatingFileHandler

logfile = 'path/to/logdir/MyName.log'
loglevel=logging.DEBUG
backupcount = 7
logformat='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'

log = logging.getLogger()
formatter = logging.Formatter(fmt=logformat)
loghandler = CTimedRotatingFileHandler(logfile, when='midnight', interval=1, backupCount=backupcount)
loghandler.setFormatter(formatter)
logging.root.addHandler(loghandler)
logging.root.setLevel(loglevel)

log.info('This is an information.')
```

## Development and building
### Prerequesites
- Python 3.9 has to be installed with `pip` and packages:
  - `virtualenv`
  - `build`

### Setup development environment
After cloning the repo, you should create a virtual environment for all further development work.  
This may be done by calling one of the included `setup_venv` scripts for your platform:
- `setup_venv.cmd`: Windows batch
- `setup_venv.ps1`: Windows Powershell
- `setup_venv.sh`: Bash

This will
- create a new virtual environment in the directory `venv` or update an existing one, 
- install all requirements from `requirements.txt`.

You still have to activate the venv manually (or automatically by configuring it in your IDE).

### Building the package
All buils settings are inside `pyproject.toml`.  
You might want to change `project.version` before building (eg. add `.dev1` to it), so you always know which one
you are dealing with.

To build the project, simply run this command from inside the project directory (the same directory that contains 
`pyproject.toml`):
```
python -m build
```

This will create `.whl` and `.tar.gz` in the directory `dist`.
