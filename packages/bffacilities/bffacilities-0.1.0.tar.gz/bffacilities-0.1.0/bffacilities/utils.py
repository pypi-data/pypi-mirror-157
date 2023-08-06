__version__ = "0.3.0"

import platform
import os
import os.path as osp
import atexit
import logging
import sys

_LOG_DIR = osp.abspath(osp.expanduser("~/.bfp/.logs"))
os.makedirs(_LOG_DIR, exist_ok=True)

formaterStr = "%(asctime)s %(levelname)s:  %(message)s"

_customLogger = {}

def createLogger(name: str, savefile = True, stream = False, 
    level = logging.INFO, basedir = None,  **kwargs):
    """
    @deprecated use setup_logger instead
    create logger
    Args: 
        name : suffix will be appended, for example, `test` will be `test.log`
        basedir: default is `~/.logs`

    kwargs:
        timeformat: default is "%Y-%m-%d %H:%M:%S" 
    :: logger_prefix deprecated ::

    """
    global _customLogger
    if name in _customLogger:
        return _customLogger[name]
    logger = logging.Logger(name)
    _customLogger[name] = logger
    tformat = kwargs.get("timeformat", "%Y-%m-%d %H:%M:%S")
    _formater = logging.Formatter(formaterStr, tformat)
    print("Warning, this function has been deprecated, use setup_logger instead")

    if savefile:
        if basedir is None:
            basedir = _LOG_DIR
        elif type(basedir) == str:
            basedir = osp.abspath(basedir)
        os.makedirs(basedir, exist_ok=True)
        if not name.endswith(".log"):
            name = name + ".log"
        log_file = osp.join(basedir, name)
        fh = logging.FileHandler(log_file, encoding="utf8")
        fh.setFormatter(_formater)
        fh.setLevel(level)
        logger.addHandler(fh)
        # print("add file handler", log_file)
    if stream:
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(_formater)
        logger.addHandler(sh)
    logger.setLevel(level)
    return logger

def changeLoggerLevel(logger, level):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
import functools
from termcolor import colored
class _ColorfulFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self._root_name = kwargs.pop("root_name") + "."
        self._abbrev_name = kwargs.pop("abbrev_name", "")
        if len(self._abbrev_name):
            self._abbrev_name = self._abbrev_name + "."
        super(_ColorfulFormatter, self).__init__(*args, **kwargs)

    def formatMessage(self, record):
        record.name = record.name.replace(self._root_name, self._abbrev_name)
        log = super(_ColorfulFormatter, self).formatMessage(record)
        if record.levelno == logging.WARNING:
            prefix = colored("WARNING", "red", attrs=["blink"])
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            prefix = colored("ERROR", "red", attrs=["blink", "underline"])
        else:
            return log
        return prefix + " " + log


@functools.lru_cache()  # so that calling setup_logger multiple times won't add many handlers
def setup_logger(
    output=None, *, color=True, name="bff", abbrev_name=None
):
    """
    Args:
        output (str): a file name or a directory to save log. If None, will not save log file.
            If ends with ".txt" or ".log", assumed to be a file name.
            Otherwise, logs will be saved to `output/log.txt`.
        name (str): the root module name of this logger
        abbrev_name (str): an abbreviation of the module, to avoid long names in logs.
            Set to "" to not log the root module in logs.
            By default, will abbreviate "detectron2" to "d2" and leave other
            modules unchanged.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if abbrev_name is None:
        abbrev_name = "d2" if name == "detectron2" else name

    # stdout logging: master only
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)
    plain_formatter = logging.Formatter(
        "[%(asctime)s] %(name)s %(levelname)s: %(message)s", datefmt="%m/%d %H:%M:%S"
    )
    if color:
        formatter = _ColorfulFormatter(
            colored("[%(asctime)s %(name)s]: ", "green") + "%(message)s",
            datefmt="%m/%d %H:%M:%S",
            root_name=name,
            abbrev_name=str(abbrev_name),
        )
    else:
        formatter = plain_formatter
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # file logging: all workers
    if output is not None:
        if output.endswith(".txt") or output.endswith(".log"):
            filename = output
        else:
            filename = osp.join(output, "log.txt")

        os.makedirs(osp.dirname(filename), exist_ok=True)

        fh = logging.StreamHandler(_cached_log_stream(filename))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(plain_formatter)
        logger.addHandler(fh)

    return logger

_opened_stream = []
def clear_streams():
    for s in _opened_stream:
        try:
            s.close()
        except:
            pass
@functools.lru_cache(maxsize=None)
def _cached_log_stream(filename):
    f = open(filename, "a")
    global _opened_stream
    if len(_opened_stream) == 0:
        atexit.register(clear_streams)
    _opened_stream.append(f)
    return f


from time import sleep
class MyProcessPool():
    def __init__(self, size = 4) -> None:
        self.size = size
        assert size > 0
        self._processes = []
        self._close = False
        self.idx = 0
        self._running = 0

    def append(self, process):
        if self._close:
            return
        self._processes.append(process)
    def _start(self):
        if self.idx >= len(self._processes):
            return
        p = self._processes[self.idx]
        self.idx += 1
        self._running += 1
        p.start()
        return p
    def start(self):
        waitting = []
        # bar = tqdm(total=len(self._processes))
        while self.idx < len(self._processes):
            for i in range(self._running, self.size):
                if self.idx >= len(self._processes):
                    continue
                p = self._start()
                waitting.append(p)
            
            while len(waitting) == self.size:
                alives = []
                for w in waitting:
                    w.join(1)
                    if w.is_alive():
                        alives.append(w)
                waitting = alives
                self._running = len(waitting)
            sleep(1)
            # print(self._running)

    def close(self):
        self._close = True
    def join(self):
        for p in self._processes:
            p.join()


## ********** For Translating **************
_LANGUAGE_DIR = osp.abspath(osp.join(osp.dirname(__file__), "locale"))
import gettext
def initGetText(domain="myfacilities", dirs = _LANGUAGE_DIR) -> gettext.gettext:
    """make some configurations on gettext module 
    for convenient internationalization
    """
    gettext.bindtextdomain(domain, dirs)
    gettext.textdomain(domain)
    gettext.find(domain, "locale", languages=["zh_CN", "en_US"])
    return gettext.gettext
## ********** For Translating **************

def lockfile(fileName, start = None, stop = None, logger=None):
    """
    original : Fix Multiple instances of scheduler problem  
        https://github.com/viniciuschiele/flask-apscheduler/issues/51
    :param str filename: specified lock filename, such as app.lock
    :param function start: callback for app loop start
    :param function stop: callback for app loop stop
    :@Return True success
    """
    if logger is None:
        logger = logging.getLogger("bffacilities")
    if platform.system() != 'Windows':
        fcntl = __import__("fcntl")
        f = open(fileName, "wb")
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if start is not None:
                start()
            # logger.debug("Scheduler Started...")
        except Exception as e:
            logger.error('Exit the scheduler, error - {}'.format(e))
            if stop is not None:
                stop()
            return False
        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
        atexit.register(unlock)
    else:
        msvcrt = __import__("msvcrt")
        f = open(fileName, "wb")
        logger.info("Lock file is: ", osp.realpath(f.name))
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            if start is not None:
                start()
            # logger.debug("Scheduler Started...")
        except Exception as e:
            logger.error('Exit the scheduler, error - {}'.format(e))
            if stop is not None:
                stop()
            return False
        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                f.close()
                os.remove(f.name)
            except IOError:
                raise
        atexit.register(_unlock_file)
    return True

import hashlib
def simplePasswordEncry(password):
    t = hashlib.sha256(password.encode())
    d = t.digest()
    return ''.join(('{:02x}'.format(x) for x in d))

import subprocess
from ._constants import BFF_OTHER_PATH
def createShortCut(target, link = None, desc="", workingdir=None, desktop=None, startup=None):
    """target: Path Lick
    """
    scriptPath = BFF_OTHER_PATH / "winbat" / "createshortcut.js"
    assert link is not None or desktop is not None or startup is not None
    if workingdir is None:
        assert osp.exists(target)
        workingdir = osp.abspath(osp.join(target, ".."))
    script = ["wscript.exe", str(scriptPath), 
        "--workingdir", str(workingdir),
        "--target", str(target),
        "--desc", desc,
        ]
    if desktop is not None:
        script.append("--desktop")
        script.append(desktop)
    if startup is not None:
        script.append("--startup")
        script.append(startup)

    try:
        process = subprocess.Popen(script, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # ret = p.stdout.read().decode()
    except Exception as e:
        logger = logging.getLogger("bffacilities")
        logger.warn(f"Error when creating shortcut {e} for {script}")
