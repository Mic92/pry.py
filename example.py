import pry


def main():
    with pry:
        raise Exception("foo")


with pry:
    raise Exception("foo")
