import pry
import xml.etree.ElementTree as ET


def foo():
    b = 1
    pry()


def main():
    a = 1
    foo()


main()

with pry():
    raise Exception("foo")

