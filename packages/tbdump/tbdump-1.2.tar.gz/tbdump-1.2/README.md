# tbdump Package

tbdump - display helpful information for debbugging in case of errors/exceptions

# DESCRIPTION

This manual page documents **tbdump** module, a Python module that displays
detailed information, which should be useful for debugging, when the Python
interpreter is aborted due to errors or traps.

Python displays minimal information in case of errors such as the type of
exception and the line number of the source code where the program execution
is terminated.  **tbdump** replaces the Python's hook `sys.excepthook` which
will be called when an exception is occured, so that more detailed information
on the program status (i.e., the location at which the exception occurred, all
variables and objects as well as their attributes defined in the scope), which
significantly helps your debugging.

Also, at the exception, **tbdump** invokes **pdb**, Python debugger.  So, you
can freely examine the state of the program using many **pdb** debugger
commands.

# EXAMPLE

By default, Python tells little about the error.

test.py:

```python
import sys
from collections import namedtuple

Record = namedtuple('Record', 'name year size note')
x = Record('John', 2019, 123, 'Good')
y = Record('Mike', 2018, 456)
```

```sh
$ python3 test.py
Traceback (most recent call last):
  File "test.py", line 6, in <module>
    y = Record('Mike', 2018, 456)
TypeError: __new__() missing 1 required positional argument: 'note'
```

With **tbdump**, you can have details.

test-tbdump.py:

```python
import sys
from collections import namedtuple

import tbdump

Record = namedtuple('Record', 'name year size note')
x = Record('John', 2019, 123, 'Good')
y = Record('Mike', 2018, 456)
```

```sh
$ python3 test-tbdump.py
---- <module> test-tbdump.py
    4 import tbdump
    5 
    6 Record = namedtuple('Record', 'name year size note')
    7 x = Record('John', 2019, 123, 'Good')
    8 y = Record('Mike', 2018, 456)
              Record = <class '__main__.Record'>
                     _asdict <function Record._asdict at 0x7f31ee2ff400>
                     _fields ('name', 'year', 'size', 'note')
            _fields_defaults {}
                       _make <classmethod object at 0x7f31ee55dc18>
                    _replace <function Record._replace at 0x7f31ee2ff2f0>
                        name <property object at 0x7f31efa665e8>
                        note <property object at 0x7f31ee2eac78>
                        size <property object at 0x7f31ee2eac28>
                        year <property object at 0x7f31efa66638>
                     __doc__ 'Record(name, year, size, note)'
              __getnewargs__ <function Record.__getnewargs__ at 0x7f31ee2ff488>
                  __module__ '__main__'
                     __new__ <staticmethod object at 0x7f31ee2fe320>
                    __repr__ <function Record.__repr__ at 0x7f31ee2ff378>
                   __slots__ ()
          namedtuple = <function namedtuple at 0x7f31efa519d8>
                 sys = ...
              tbdump = <module 'tbdump' from '/pub/home/ohsaki/lib/python/tbdump.py...
                      _print <function _print at 0x7f31efa51598>
                   linecache <module 'linecache' from '/usr/local/stow/python/lib...
                        main <function main at 0x7f31ee2ff1e0>
                         pdb <module 'pdb' from '/usr/local/stow/python/lib/pytho...
                   print_exc <function print_exc at 0x7f31ee2ff158>
                    print_tb <function print_tb at 0x7f31ee2ff0d0>
                         sys <module 'sys' (built-in)>
                        term <module 'ansiterm' from '/usr/local/stow/python/lib/...
                   traceback <module 'traceback' from '/usr/local/stow/python/lib...
                 trimmed_str <function trimmed_str at 0x7f31ee2ff048>
                __builtins__ {'__name__': 'builtins', '__doc__': "Built-in functi...
                  __cached__ '/pub/home/ohsaki/lib/python/__pycache__/tbdump.cpyt...
                     __doc__ None
                    __file__ '/pub/home/ohsaki/lib/python/tbdump.py'
                  __loader__ <_frozen_importlib_external.SourceFileLoader object ...
                    __name__ 'tbdump'
                 __package__ ''
                    __spec__ ModuleSpec(name='tbdump', loader=<_frozen_importlib_...
                   x = Record(name='John', year=2019, size=123, note='Good')
     __annotations__ = {}
        __builtins__ = ...
          __cached__ = None
             __doc__ = None
            __file__ = '/tmp/4.py'
          __loader__ = <_frozen_importlib_external.SourceFileLoader object at 0x7f3...
                        name '__main__'
                        path '/tmp/4.py'
            __name__ = '__main__'
         __package__ = None
            __spec__ = None
TypeError: __new__() missing 1 required positional argument: 'note'

> test-tbdump.py(8)<module>()
-> y = Record('Mike', 2018, 456)
(Pdb) 
```

You are now in the **pdb** debugger.  You can examine the internals:

```sh
(Pdb) x
Record(name='John', year=2019, size=123, note='Good')
(Pdb) x.name
'John'
(Pdb) Record
<class '__main__.Record'>
(Pdb) list
  3  	
  4  	import tbdump
  5  	
  6  	Record = namedtuple('Record', 'name year size note')
  7  	x = Record('John', 2019, 123, 'Good')
  8  ->	y = Record('Mike', 2018, 456)
[EOF]
(Pdb) 
```

# INSTALLATION

```python
pip3 install tbdump
```

# AVAILABILITY

The latest version of **tbdump** module is available at
PyPI (https://pypi.org/project/tbdump/) .

# SEE ALSO

pdb - The Python Debugger (https://docs.python.org/3.7/library/pdb.html)

traceback - Print or retrieve a stack traceback (https://docs.python.org/3.7/library/traceback.html)

# AUTHOR

Hiroyuki Ohsaki <ohsaki[atmark]lsnl.jp>
