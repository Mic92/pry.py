import code
import inspect
import os,sys

try:
    import bpython
    has_bpython = True
except ImportError:
    has_bpython = False
    try:
        import IPython
        has_ipython = True
    except ImportError:
        has_ipython = False
        pass

try:
    import pygments
    import pygments.lexers
    import pygments.formatters
    has_pygments = True
except ImportError:
    has_pygments = False
    pass

try:
    import readline
    has_readline = True
except ImportError:
    has_readline = False
    pass
else:
    import rlcompleter

class Pry():
    def __init__(self,module):
        self.module = module

    def highlight(self, lines):
        pygments = self.module.pygments
        tokens = pygments.lexers.PythonLexer().get_tokens("\n".join(lines))
        source = pygments.format(tokens, pygments.formatters.TerminalFormatter())
        return source.split("\n")

    def get_context(self, currentframe):
        frame,filename,line_number,function_name,lines,index=\
                self.module.inspect.getouterframes(currentframe)[1]
        before = max(line_number - 6,0)
        after = line_number + 4
        context = []
        try:
            f = open(filename)

            for i, line in enumerate(f):
                if i >= before:
                    context.append(line.rstrip())
                if i > after:
                    break
            f.close()
        except IOError:
            context = lines
        banner = "From: {} @ line {} :\n".format(filename,line_number)
        i = max(line_number - 5, 0)

        if self.module.has_pygments and not self.module.has_bpython:
            context = self.highlight(context)

        for line in context:
            pointer = "-->" if i == line_number else "   "
            banner += "{} {}: {}\n".format(pointer, i, line)
            i += 1
        return banner, frame.f_locals

    def shell(self, context, local):
        module = self.module
        if self.module.has_bpython:
            module.bpython.embed(local,banner=context)
        if self.module.has_ipython:
            module.IPython.embed(user_ns=local, banner1=context)
        else:
            if self.module.has_readline:
                module.readline.parse_and_bind("tab: complete")
            module.code.interact(context,local = local)

    def __call__(self):
        currentframe = self.module.inspect.currentframe()
        context, local = self.get_context(currentframe)
        self.shell(context, local)

# hack for convenient access
sys.modules[__name__] = Pry(sys.modules[__name__])
