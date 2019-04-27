import functools
import importlib
import pdb
import sys
import traceback

import click


def import_object(import_path):
    modulename, objname = import_path.rsplit(":", 1)
    module = importlib.import_module(modulename)
    return getattr(module, objname)


class DebuggerManager:

    pdbcls = pdb.Pdb
    debug = None

    def _handle_debug_flag(self, ctx, param, value):
        if value is not None:
            self.debug = value

    def debug_flag(self, *param_decls, **attrs):
        if not param_decls:
            param_decls = ("--pdb/--no-pdb",)

        defaults = dict(help="Enable/disable debugger; i.e., drop in to pdb on error.")

        return click.option(
            *param_decls,
            callback=self._handle_debug_flag,
            default=None,
            expose_value=False,
            **dict(defaults, **attrs)
        )

    def _handle_debugger_option(self, ctx, param, value):
        if value is None:
            return
        if self.debug is None:
            self.debug = True
        import_path = {
            "pdb": "pdb:Pdb",
            "ipdb": "IPython.terminal.debugger:TerminalPdb",
            "pudb": " pudb.debugger:Debugger",
        }.get(value, value)
        self.pdbcls = import_object(import_path)

    def debugger_option(self, *param_decls, **attrs):
        if not param_decls:
            param_decls = ("--pdbcls",)

        defaults = dict(
            metavar="MODULE:CLASS",
            help=(
                "Specify interactive Python debugger to be used."
                " For example: --pdbcls=IPython.terminal.debugger:TerminalPdb."
                " Short hand `pdb`, `ipdb`, and `pudb` can also be used."
            ),
        )

        return click.option(
            *param_decls,
            callback=self._handle_debugger_option,
            expose_value=False,
            **dict(defaults, **attrs)
        )

    def install_options(self):
        def decorator(f):
            f = self.debug_flag()(f)
            f = self.debugger_option()(f)
            return f

        return decorator

    def command(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except Exception:
                traceback.print_exc()
                if self.debug:
                    self.post_mortem()
                raise

        return wrapper

    def post_mortem(self):
        # See also `_pytest.debugging.post_mortem`
        p = self.pdbcls()
        p.reset()
        p.interaction(None, sys.exc_info()[2])


make_debuggable = DebuggerManager
debuggable = DebuggerManager()
