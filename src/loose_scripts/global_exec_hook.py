import bpy, os, sys, traceback

_OLD_EXCEPTHOOK = sys.excepthook

def log_crash(atype, value, tb):
    global _OLD_EXCEPTHOOK  # pylint: disable=W0602
    stacktrace = "\n"
    for line in traceback.extract_tb(tb).format():
        stacktrace = stacktrace + line
    print("Unhandled crash: " + stacktrace + "\n" + str(value) + "\n")
    if _OLD_EXCEPTHOOK:
        _OLD_EXCEPTHOOK(atype, value, tb)
     
sys.excepthook = log_crash   

