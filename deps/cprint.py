#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com/
#

#
# colors ######################################################################
#

class Colors:
    RESET = '\u001b[0m'
    WARN = '\u001b[33m'
    ERR = '\u001b[41m\u001b[37m'
    INFO = '\u001b[36m'
    SUCCESS = '\u001b[32m'

#
# print #######################################################################
#

def warn(*args):
    print(Colors.WARN,*args,Colors.RESET, sep='')

#
# -----------------------------------------------------------------------------
#

def err(*args):
    print(Colors.ERR,*args,Colors.RESET, sep='')

#
# -----------------------------------------------------------------------------
#

def info(*args):
    print(Colors.INFO,*args,Colors.RESET, sep='')

#
# -----------------------------------------------------------------------------
#

def success(*args):
    print(Colors.SUCCESS,*args,Colors.RESET, sep='')

