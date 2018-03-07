import code
import inspect
import sys
import traceback
from contextlib import contextmanager
from bdb import BdbQuit

BdbQuit_excepthook = None
try:
    import bpython
    has_bpython = True
except ImportError:
    has_bpython = False
    try:
        import IPython
        from IPython.core.debugger import BdbQuit_excepthook
        from IPython.terminal.interactiveshell import TerminalInteractiveShell
        # super hacky, but nobody got time for this!
        TerminalInteractiveShell.confirm_exit = False
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
    def __init__(self, module):
        self.module = module
        self.lexer = None
        self.formatter = None

    def highlight(self, lines):
        if not self.module.has_pygments:
            return lines
        p = self.module.pygments
        if self.lexer is None:
            self.lexer = p.lexers.PythonLexer()
        if self.formatter is None:
            self.formatter = p.formatters.Terminal256Formatter()
        tokens = self.lexer.get_tokens("\n".join(lines))
        source = p.format(tokens, self.formatter)
        return source.split("\n")

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        self.wrap_sys_excepthook()
        while tb.tb_next is not None:
            context, local = self.get_context(tb.tb_frame)
            self.module.sys.stderr.write(context)
            tb = tb.tb_next
        self.module.sys.stderr.write("%s: %s\n" % (type.__name__, str(value)))
        self(tb.tb_frame)

    def wrap_sys_excepthook(self):
        m = self.module
        if not m.has_ipython:
            return
        # make sure we wrap it only once or we would end up with a cycle
        #  BdbQuit_excepthook.excepthook_ori == BdbQuit_excepthook
        if m.sys.excepthook != m.BdbQuit_excepthook:
            m.BdbQuit_excepthook.excepthook_ori = m.sys.excepthook
            m.sys.excepthook = m.BdbQuit_excepthook

    def get_context(self, currentframe):
        frames = self.module.inspect.getouterframes(currentframe)
        if len(frames) > 1:
            frames = frames[1:]
        frame, filename, line_number, function_name, lines, index = frames[0]
        before = max(line_number - 6, 0)
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
        banner = "From: {} @ line {} :\n".format(filename, line_number)
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
            module.bpython.embed(local, banner=context)
        if self.module.has_ipython:
            module.IPython.embed(user_ns=local, banner1=context)
        else:
            if self.module.has_readline:
                module.readline.parse_and_bind("tab: complete")
            module.code.interact(context, local=local)

    def __call__(self, frame=None):
        if frame is None:
            frame = self.module.inspect.currentframe()
        context, local = self.get_context(frame)
        self.shell(context, local)


# hack for convenient access
sys.modules[__name__] = Pry(sys.modules[__name__])
