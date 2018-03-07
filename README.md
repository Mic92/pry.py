pry.py - an interactive drop in REPL for python

EXAMPLE
=======

Allow to embed ipython/bpython or the builtin python shell in your projects

![Example](http://i.imgur.com/ey1vF8O.png)

USAGE
=====

```python
import pry; pry()
```

Debug programs when exceptions are thrown:

```python
import pry
def faulty():
    raise Exception("foo")
with pry:
    faulty()
```

INSTALL
=======

```
$ curl https://raw.githubusercontent.com/Mic92/pry.py/master/pry.py > pry.py
```

or:

```
pip install git+https://github.com/Mic92/pry.py
```
