import code
import inspect
import sys
import traceback
import tempfile
import re
import shutil
from bdb import BdbQuit

try:
    import termios
except ImportError:
    termios = None

try:
    import pygments
    import pygments.lexers
    import pygments.formatters
    has_pygments = True
except ImportError:
    has_pygments = False
    pass

BdbQuit_excepthook = None
try:
    import bpython
    has_bpython = True
except ImportError:
    has_bpython = False
    try:
        import IPython
        from IPython.core.debugger import BdbQuit_excepthook
        from IPython.core import page
        from IPython.terminal.ipapp import load_default_config
        from IPython.core.magic import (magics_class, line_magic, Magics)

        ipython_config = load_default_config()
        ipython_config.TerminalInteractiveShell.confirm_exit = False

        old_init = IPython.terminal.embed.InteractiveShellEmbed.__init__

        def new_init(self, *k, **kw):
            old_init(self, *k, **kw)
            from pry import get_context, highlight

            class Frame():
                """
                Abstraction around old python traceback api
                """
                def __init__(self, *args):
                    self.frame = args[0]
                    self.filename = args[1]
                    self.lineno = args[2]
                    self.function = args[3]
                    self.lines = args[4]
                    self.index = args[5]

            # XXX also use this in pry wrapper
            def inspect_frames():
                frames = []
                raw_frames = inspect.getouterframes(inspect.currentframe())
                for raw_frame in raw_frames:
                    frames.append(Frame(*raw_frame))
                return frames

            @magics_class
            class MyMagics(Magics):
                def __init__(self, shell):
                    # You must call the parent constructor
                    super(MyMagics, self).__init__(shell)

                    found_pry = False
                    self.frames = inspect_frames()
                    for (i, frame) in enumerate(self.frames):
                        if frame.filename.endswith("pry.py"):
                            if frame.function in ("__call__", "__exit__"):
                                found_pry = True
                        elif found_pry:
                            break
                    self.frame_offset = i
                    self.calling_frame = frame

                @line_magic("editfile")
                def editfile(self, query):
                    """
                    Open current breakpoint in editor.
                    """
                    f = self.frames[self.frame_offset]
                    IPython.get_ipython().hooks.editor(
                        f.filename, linenum=f.lineno)

                @line_magic("where")
                def where(self, query):
                    """
                    Show backtrace
                    """
                    context = []
                    for f in self.frames[self.frame_offset:]:
                        context.append(get_context(f.frame)[0])
                    page.page("".join(context))

                @line_magic("showsource")
                def showsource(self, query):
                    """
                    Show source of object
                    """
                    f = self.frames[self.frame_offset].frame
                    obj = f.f_locals.get(query, f.f_globals.get(query, None))
                    if obj is None:
                        return "Not found: %s" % query
                    s = inspect.getsource(obj)
                    if has_pygments:
                        s = "\n".join(highlight(s.split("\n")))
                    page.page(s)

                def update_context(self):
                    f = self.frames[self.frame_offset].frame
                    context, local, global_ = get_context(f)
                    sys.stderr.write(context)
                    # hacky
                    self.shell.user_ns.update(local)
                    self.shell.user_module.__dict__ = global_

                @line_magic("up")
                def up(self, query):
                    """
                    Get from call frame up.
                    """
                    self.frame_offset += 1
                    self.frame_offset = min(self.frame_offset,
                                            len(self.frames) - 1)
                    self.update_context()

                @line_magic("down")
                def down(self, query):
                    """
                    Get from call frame down.
                    """
                    self.frame_offset -= 1
                    self.frame_offset = max(self.frame_offset, 0)
                    self.update_context()

                @line_magic("removepry")
                def removepry(self, query):
                    """
                    Remove pry call at current breakpoint.
                    """
                    f = self.calling_frame
                    with open(f.filename) as src, \
                            tempfile.NamedTemporaryFile(mode='w') as dst:
                        for i, line in enumerate(src):
                            if (i + 1) == f.lineno:
                                line = re.sub(r'(import pry;)?\s*pry\(\)', "",
                                              line)
                                if line.strip() == "":
                                    continue
                            dst.write(line)
                        dst.flush()
                        src.close()
                        shutil.copyfile(dst.name, f.filename)

            self.register_magics(MyMagics(self))

        IPython.terminal.embed.InteractiveShellEmbed.__init__ = new_init

        has_ipython = True
    except ImportError:
        has_ipython = False
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
            context = self.get_context(tb.tb_frame)[0]
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
        return banner, frame.f_locals, frame.f_globals

    def fix_tty(self):
        m = self.module
        if m.termios is None:
            return
        # Sometimes when you do something funky, you may lose your terminal
        # echo. This should restore it when spawning new pdb.
        termios_fd = m.sys.stdin.fileno()
        termios_echo = m.termios.tcgetattr(termios_fd)
        termios_echo[3] = termios_echo[3] | m.termios.ECHO
        m.termios.tcsetattr(termios_fd, termios.TCSADRAIN, termios_echo)

    def shell(self, context, local, global_):
        m = self.module
        if m.has_bpython:
            globals = global_
            m.bpython.embed(local, banner=context)
        if m.has_ipython:
            m.IPython.embed(
                user_ns=local,
                global_ns=global_,
                banner1=context,
                config=m.ipython_config)
        else:
            if m.has_readline:
                m.readline.parse_and_bind("tab: complete")
            globals = global_
            m.code.interact(context, local=local)

    def __call__(self, frame=None):
        if frame is None:
            frame = self.module.inspect.currentframe()
        context, local, global_ = self.get_context(frame)
        self.fix_tty()
        self.shell(context, local, global_)


# hack for convenient access
sys.modules[__name__] = Pry(sys.modules[__name__])
