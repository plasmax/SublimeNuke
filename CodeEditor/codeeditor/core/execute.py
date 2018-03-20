from __main__ import __dict__
import traceback
import sys
import inspect
from pprint import pprint

def mainexec(text, wholeText):
    """
    Code execution in top level namespace.
    Reformats exceptions to remove 
    references to this file.
    """
    if len(text.strip().split('\n')) == 1:
        mode = 'single'
    else:
        mode = 'exec'

    try:
        _code = compile(text, '<i.d.e>', mode)
    except SyntaxError:
        print_syntax_traceback()
        return

    _ = __dict__.copy()
    print('# Result: ')
    try:
        # Ian Thompson is a golden god
        exec(_code, __dict__)
    except Exception:
        print_traceback(wholeText)
    else:
        __dict__.update(_)
        if mode == 'single': 
            for value in __dict__.values():
                if  value not in _.values():
                    print(value)

def print_syntax_traceback():
    """
    Strip out lines of the error that refer to this file.
    """
    formatted_lines = traceback.format_exc().splitlines()
    print( formatted_lines[0] )
    print( '\n'.join(formatted_lines[3:]) )

def print_traceback(wholeText):
    """
    Using the whole text of the document,
    extract the lines of code that caused the error
    and print them in the normal traceback format.
    """
    textlines = wholeText.splitlines()
    

    print('Traceback (most recent call last):')
    msg = '  File "{0}", line {1}, in {2}\n    {3}'
    _, _, exc_tb = sys.exc_info()
    for file, lineno, scope, code in traceback.extract_tb(exc_tb):
        if code is None:
            tracemsg = msg.format(file, lineno, scope, textlines[lineno-1].strip())
            print(tracemsg)

    formatted_lines = traceback.format_exc().splitlines()
    print formatted_lines[-1]