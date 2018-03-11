import pry
import xml.etree.ElementTree as ET


class Obj():
    def __init__(self):
        self.attr = 1

    def baz(self):
        c = 1
        pry()


def bar():
    b = 1
    Obj().baz()
    with pry():
         raise Exception("foo")


def foo():
    a = 1
    bar()


def main():
    a = Obj()
    foo()


main()

