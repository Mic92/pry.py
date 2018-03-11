# pry.py - an interactive drop in REPL for python

## EXAMPLE

Allow to embed ipython/bpython or the builtin python shell in your projects

![Example](http://i.imgur.com/ey1vF8O.png)

## FEATURES

- works with python2.7/python3
- optional syntax highlighting (requires pygments)
- auto completion
- In IPython also the following magics (commands) are defined:
  - `up/down`: Navigate in the call stack up/down
  - `where`: Show a backtrace of the current breakpoint
  - `removepry`: Remove current breakpoint from file
  - `showsource`: show python source of object
  - `editfile`: open editor at current breakpoint
  - `ls`: show properties/methods/local variables, can be also called on objects

## USAGE

```python
import pry; pry()
```

Spawn a REPL when exceptions are thrown:

```python
import pry
def faulty():
    raise Exception("foo")
with pry:
    faulty()
```

## INSTALL

```
$ curl https://raw.githubusercontent.com/Mic92/pry.py/master/pry.py > pry.py
```

or:

```
pip install git+https://github.com/Mic92/pry.py
```
