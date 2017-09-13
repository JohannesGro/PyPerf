
"""Benchmark tool
"""


import argparse
from argparse import RawTextHelpFormatter
import pkg_resources


class Benchmark(object):
    def __init__(self):
        self.subcommands = {}
        for ep in pkg_resources.iter_entry_points("benchmarktool"):
            self.subcommands[ep.name] = ep.load()

    def _main(self, args):
        cmdname = args.command[0]
        cmdclass = self.subcommands.get(cmdname, None)
        if cmdclass is None:
            parser.error("Unknown subcommand %s" % cmdname)
        else:
            cmd = cmdclass(args.commandargs)
            try:
                return cmd.main()
            except RuntimeError as exc:
                print(exc)


def main():
    bm = Benchmark()
    global parser
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group('Available subcommands')
    for subc in sorted(bm.subcommands.items()):
        group.add_argument(subc[0], help=subc[1].__doc__)
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Argument list for the sub command to run.")
    # Grab the self.args from argv
    args = parser.parse_args()
    return bm._main(args)
