import pry
import xml.etree.ElementTree as ET


class Obj():
    attr = 1


def baz():
    c = 1
    pry()


def bar():
    b = 1
    baz()


def foo():
    a = 1
    bar()


def main():
    a = Obj()
    foo()


main()

with pry():
    raise Exception("foo")
