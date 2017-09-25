
"""Benchmark tool
"""
import argparse
import pkg_resources


class Benchmark(object):
    def __init__(self):
        self.subcommands = {}
        for ep in pkg_resources.iter_entry_points("benchmarktool"):
            self.subcommands[ep.name] = ep.load()

    def _main(self, args):
        cmdname = args.__dict__.pop('command', None)
        import sys
        cmdclass = self.subcommands.get(cmdname, None)
        if cmdclass is None:
            parser.error("Unknown subcommand %s" % cmdname)
        else:
            cmd = cmdclass(args)
            try:
                return cmd.main()
            except RuntimeError as exc:
                print(exc)


def main():
    bm = Benchmark()
    global parser
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='Available subcommands')
    for subc in sorted(bm.subcommands.items()):
        command = subparsers.add_parser(subc[0], help=subc[1].__doc__)
        command.set_defaults(command=subc[0])
        for action in subc[1].parser._actions:
            if type(action) == argparse._StoreAction:
                command._add_action(action)
    #subparsers.add_argument("args", nargs=argparse.REMAINDER, help="Argument list for the sub command to run.")
    # Grab the self.args from argv
    args = parser.parse_args()
    return bm._main(args)
